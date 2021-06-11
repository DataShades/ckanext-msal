import logging
import secrets

import requests


from typing import Any, NamedTuple, Optional, List

import ckan.plugins.toolkit as tk
import ckan.model as model


import ckan.plugins.toolkit as tk
from ckan.common import g

import ckanext.msal.config as msal_conf
import ckanext.msal.utils as msal_utils


log = logging.getLogger(__name__)


def is_user_disabled(userdata: dict):
    # "accountEnabled": true,
    pass


def _login_user(user_data: dict) -> None:
    return get_or_create_user(user_data["oid"])


def get_or_create_user(user_id: str) -> model.User:
    """Returns an existed user by user_id or
    creates a new one from user_data,
    that fetches from Microsoft Graph API

    user_id: str = user ID
    """

    # What if user has been disabled on MS org?
    # I need to disable it here too / or delete
    # So Looks like I need to call get_msal_user_data before?
    # TODO
    user: model.User = model.User.get(user_id)

    if not user:
        user_data: dict = get_msal_user_data()
        user: model.User = _create_user_from_user_data(user_data)

    return user


def get_msal_user_data() -> dict:
    token: List[str] = msal_utils._get_token_from_cache(msal_conf.SCOPE)
    if not token:
        return {}

    resp = requests.get(
        msal_conf.USERS_ENDPOINT,
        headers={
            'Authorization': 'Bearer ' + token['access_token']
        },
        # TODO: need to clarify which fields I need in future
        # params={
        #     '$select': 'identities,displayName,mail'
        # }
    )
    resp.raise_for_status()
    return resp.json()['value'][0]


def _create_user_from_user_data(user_data: dict) -> dict:
    """Create a user with random password using Microsoft Graph API's data.

    Raises:
    ValidationError if email is not unique
    """

    user: dict = {
        "id": user_data.get('id'),
        "email": user_data.get('mail'),
        "name": _sanitize_username(user_data.get('userPrincipalName')),
        "password": _make_password(),
    }

    user: model.User = tk.get_action("user_create")(
        {"ignore_auth": True, "user": ""}, user
    )
    return user


def _sanitize_username(username: str) -> str:
    # "mail": "MeganB@M365x214355.onmicrosoft.com",
    # "userPrincipalName": "MeganB@M365x214355.onmicrosoft.com",
    # "mailNickname": "MeganB",
    return username.split('@')[0]


def _make_password() -> str:
    return secrets.token_urlsafe(60)
