from typing import Dict, Optional, Any
from datetime import datetime as dt
import logging

import requests
from faker import Faker

import ckan.plugins.toolkit as tk
import ckan.logic as logic

import ckanext.msal.config as msal_conf
import ckanext.msal.utils as msal_utils


log = logging.getLogger(__name__)
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
    
    object_id: str = user_data["oid"]

    try:
        user: Dict[str, Any] = tk.get_action("user_show")(
            {"ignore_auth": True}, {"id": object_id}
        )
    except logic.NotFound:
        log.info(f"MSAL. User not found, creating new one.")
        user_dict = get_msal_user_data()

        if "error" in user_dict:
            log.error("MSAL. User creation failed.")
            return {}
        return _create_user_from_user_data(user_dict, object_id) if user_dict else {}

    return user


def get_msal_user_data() -> Dict[str, Any]:
    """
    Requests an additional user data from microsoft graph API

    return
    type: Dict[str, Any]
    """
    token: Optional[Dict[Any, Any]] = msal_utils._get_token_from_cache(msal_conf.SCOPE)
    if not token:
        return {}

    log.info(f"MSAL. Fetching user data from Microsoft Graph API by an access token.")
    resp = requests.get(
        USER_ENDPOINT,
        headers={"Authorization": "Bearer " + token["access_token"]},
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

    return resp.json()


def _create_user_from_user_data(user_data: dict, object_id: str) -> Dict[str, Any]:
    """Create a user with random password using Microsoft Graph API's data.

    raises
    ValidationError if email is not unique

    args
    user_data: dict - user data dict
    object_id: str - actually a `user_id` from Azure AD

    return
    type: dict
    """
    _id: str = object_id
    email: str = _get_email(user_data)
    password: str = msal_utils._make_password()
    username: str = _get_username(user_data)

    if not _is_username_unique(username):
        username = f"{username}-{dt.now().strftime('%S%f')}"

    user = tk.get_action("user_create")(
        {"ignore_auth": True, "user": username},
        {
            "id": _id,
            "email": email,
            "name": username,
            "password": password,
        },
    )
    log.info(f"MSAL. User has been created: {user['id']} - {user['name']}.")
    return user


def _get_email(user_dict: Dict[str,str,]) -> str:
    """
    Fetches email from user_data if exists, otherwise generates random email
    The `userPrincipalName` is formatted like an email address (username@onmicrosoft.com)
    """
    return user_dict.get("userPrincipalName") or user_dict.get("mail") or _make_email()


def _make_email(domain: str = "onmicrosoft.com") -> str:
    """
    Returns a random email with custom domain
    If domain is not provided uses `onmicrosoft.com`

    args
    domain: str - domain used to generate email

    return
    type: str
    """
    f = Faker()
    return f.email()


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
        tk.get_action("user_show")({"ignore_auth": True}, {"id": username})
    except logic.NotFound:
        return True

    return False


def is_user_enabled(user_dict: Dict[str, str]) -> bool:
    """
    Returns True if user is enabled

    # TODO
    Currently, we are not using this function.

    args
    user_dict: Dict[str, str] - user data dict

    return
    type: bool
    """
    return user_dict.get("accountEnabled") is True


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