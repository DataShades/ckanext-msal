from __future__ import annotations

import logging
from typing import Dict, Optional, Any
from datetime import datetime as dt

import requests
from faker import Faker
from sqlalchemy import func

import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckan.lib.mailer as mailer
from ckan.lib.munge import munge_name
from ckan.common import session
from ckan.model import User, Session

import ckanext.msal.config as conf
import ckanext.msal.utils as msal_utils


log = logging.getLogger(__name__)

user_show = tk.get_action("user_show")
user_update = tk.get_action("user_update")

USER_ENDPOINT = "https://graph.microsoft.com/beta/me"


def _login_user(user_data: dict) -> Dict[str, Any]:
    return get_or_create_user(user_data)


def get_or_create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Returns an existed user data by oid (object id) or
    creates a new one from user_data fetched from Microsoft Graph API

    args
    user_data: dict - user data dict

    {
        "displayName": "Mark Spencer",
        "givenName": "Mark",
        "mailNickname": "mark209",
        "mail": mark209@myorg.onmicrosoft.com,
        "surname": "Spencer",
        "userPrincipalName": "mark209@myorg.onmicrosoft.com",
        "id": "3f22cb88-c272-44f1-838f-f823cdc08bd6",
    }

    return
    type: Dict[str, Any]
    """

    try:
        user: Dict[str, Any] = _get_user(user_data)
    except tk.ObjectNotFound:
        log.info(f"MSAL. User not found, creating new one.")
        return _create_user_from_user_data(user_data)

    return user


def _get_user(user_data: dict[str, Any]) -> dict[str, Any]:
    """Searches for an existing user created with MSAL
    or for a user with the same email


    Args:
        user_data (dict[str, Any]): MSAL user data

    Raises:
        tk.ObjectNotFound: raises an error if there is no user

    Returns:
        dict[str, Any]: CKAN user data
    """

    user = (
        Session.query(User.id)
        .filter(User.plugin_extras["msal"]["id"].astext == str(user_data["id"]))
        .one_or_none()
    )

    if not user and tk.config.get(
        conf.MERGE_MATCHING_EMAILS, conf.MERGE_MATCHING_EMAILS_DF
    ):
        user_dict = _merge_users(user_data)

        if user_dict:
            return user_dict

    if not user:
        raise tk.ObjectNotFound(
            tk._(f"User with MSAL ID - {user_data['id']} not found")
        )

    return user_show(msal_utils.get_site_admin_context(), {"id": user.id})


def _merge_users(user_data: dict) -> Optional[dict[str, Any]]:
    user_email: str = _get_email(user_data)
    query = Session.query(User)
    _lower = func.lower if is_email_insensitive() else lambda x: x
    query = query.filter(_lower(User.email) == _lower(user_email))

    user = query.one_or_none()

    if user is None:
        return

    log.info(f"MSAL. A user with the same email has been found: {user_email}")
    log.info("MSAL. Merging users.")

    context = msal_utils.get_site_admin_context()

    user_dict = user_show(context, {"id": user.id})
    user_dict.setdefault("plugin_extras", {})

    user_dict["plugin_extras"]["msal"] = {"id": user_data["id"]}
    user_dict["password"] = msal_utils._make_password()
    user_dict["email"] = user_email

    user_obj = context["user_obj"]
    try:
        log.info(f"Emailing reset link to user: {user_obj.name}")
        mailer.send_reset_link(user_obj)
    except mailer.MailerException as e:
        # SMTP is not configured correctly or the server is
        # temporarily unavailable
        log.error(tk._("MSAL. Error sending the password reset email."))
        log.error(e)

    return user_update(context, user_dict)


def get_msal_user_data() -> Dict[str, Any]:
    """
    Requests an additional user data from microsoft graph API

    return
    type: Dict[str, Any]
    """
    token: Optional[Dict[Any, Any]] = msal_utils._get_token_from_cache(conf.SCOPE)

    access_token: str = session.get("msal_auth_flow", {}).get("access_token", "")
    if not access_token:
        token: Optional[Dict[Any, Any]] = msal_utils._get_token_from_cache(conf.SCOPE)
        access_token: str = token["access_token"] if token else ""

        if not access_token:
            return {"error": [tk._("The token has expired. Please, try again.")]}

    log.info(f"MSAL. Fetching user data from Microsoft Graph API by an access token.")
    resp = requests.get(
        USER_ENDPOINT,
        headers={"Authorization": "Bearer " + access_token},
        params={
            "$id"
            "$select": "id,displayName,userPrincipalName,mail,mailNickname,accountEnabled"
        },
    )

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        log.error(f"MSAL. Fetch failed: {resp.reason} {resp.status_code}")
        return resp.json()

    log.info(f"MSAL. Success fetch.")

    user_data: dict[str, Any] = resp.json()
    user_email: str = _get_email(user_data)

    if msal_utils.is_email_restricted(user_email) or not msal_utils.is_email_allowed(
        user_email
    ):
        log.info(
            "MSAL. User won't be created, "
            f"because of the domain policy: {user_email}"
        )

        restriction_err: str = tk.config.get(
            conf.RESTRICTION_ERR, conf.RESTRICTION_ERR_DF
        )
        raise tk.ValidationError({"email": [tk._(restriction_err)]})
    return resp.json()


def _create_user_from_user_data(user_data: dict) -> Dict[str, Any]:
    """Create a user with random password using Microsoft Graph API's data.

    raises
    ValidationError if email is not unique

    args
    user_data: dict - user data dict
    object_id: str - actually a `user_id` from Azure AD

    return
    type: dict
    """

    email: str = _get_email(user_data)
    password: str = msal_utils._make_password()
    username: str = munge_name(_get_username(user_data))

    if not _is_username_unique(username):
        username = f"{username}-{dt.now().strftime('%S%f')}"

    user = tk.get_action("user_create")(
        msal_utils.get_site_admin_context(),
        {
            "email": email,
            "name": username,
            "password": password,
            "plugin_extras": {"msal": {"id": user_data["id"]}},
        },
    )
    log.info(f"MSAL. User has been created: {user['id']} - {user['name']}.")
    return user


def _get_email(
    user_dict: Dict[
        str,
        str,
    ]
) -> str:
    """
    Fetches email from user_data if exists, otherwise generates random email
    The `userPrincipalName` is formatted like an email address (username@onmicrosoft.com)

    userPrincipalName: The user principal name (UPN) of the user.
        The UPN is an Internet-style login name for the user based on
        the Internet standard RFC 822. By convention,
        this should map to the user's email name.

    mail: The SMTP address for the user, for example, 'jeff@contoso.onmicrosoft.com'
    """
    return user_dict.get("userPrincipalName") or user_dict.get("mail") or _make_email()


def _make_email(domain: str = "msal.onmicrosoft.com") -> str:
    """
    Returns a random email with custom domain
    If domain is not provided uses `onmicrosoft.com`

    args
    domain: str - domain used to generate email

    return
    type: str
    """
    f = Faker()
    return f.email(domain)


def _get_username(user_dict: Dict[str, str]) -> str:
    """
    Fetches username from user_data if exists
    If not - munges it from userPrincipalName or mail

    args
    user_dict: Dict[str, str] - user data dict

    return
    type: str
    """
    username: Optional[str] = user_dict.get("mailNickname")

    if not username:
        username = user_dict.get("mail") or user_dict["userPrincipalName"]
        return username.split("@")[0]
    return username


def _is_username_unique(username: str) -> bool:
    try:
        user_show({"ignore_auth": True}, {"id": username})
    except logic.NotFound:
        return True

    return False


def is_user_enabled(user_dict: Dict[str, str]) -> bool:
    """
    Returns True if user is enabled

    args
    user_dict: Dict[str, str] - user data dict

    return
    type: bool
    """
    return user_dict.get("accountEnabled")


def is_user_sysadmin(user_dict: Dict[str, str]) -> bool:
    """
    Returns True if user is sysadmin

    # TODO
    Currently, we are not using this function.
    I didn't find an apropriate property to say if user is a sysadmin yet

    args
    user_dict: Dict[str, str] - user data dict

    return
    type: bool
    """
    return False


def is_email_insensitive() -> bool:
    return tk.asbool(
        tk.config.get(conf.EMAIL_CASE_INSENSITIVE, conf.EMAIL_CASE_INSENSITIVE_DF)
    )
