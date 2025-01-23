from __future__ import annotations

import secrets
from typing import Any
from datetime import datetime as dt
from datetime import timedelta as td

import msal

import ckan.types as types
import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckan.common import session

import ckanext.msal.config as conf


def build_msal_app(cache=None):
    authority: str = tk.config.get(conf.AUTHORITY, conf.AUTHORITY_DF)
    client_id: str = tk.config.get(conf.CLIENT_ID)
    client_credential: str = tk.config.get(conf.CLIENT_SECRET)

    return msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{authority}",
        client_credential=client_credential,
        token_cache=cache,
    )


def build_auth_code_flow(authority=None, scopes=None) -> dict[str, Any]:
    return build_msal_app().initiate_auth_code_flow(
        scopes or [], redirect_uri=h.url_for("msal.authorized", _external=True)
    )


def load_cache() -> msal.SerializableTokenCache:
    """Load token cache from user session

    Returns:
        Token cache
    """
    cache = msal.SerializableTokenCache()
    if session.get("msal_token_cache"):
        cache.deserialize(session["msal_token_cache"])
    return cache


def save_cache(cache: msal.SerializableTokenCache) -> None:
    """Save token cache to user session

    Args:
        cache (msal.SerializableTokenCache): Token cache
    """
    if cache.has_state_changed:
        session["msal_token_cache"] = cache.serialize()


def get_token_from_cache(scope=None) -> dict[Any, Any] | None:
    """Get token from cache

    Args:
        scope: Scope

    Returns:
        Token
    """
    cache = load_cache()
    app = build_msal_app(cache=cache)
    accounts: list[dict[Any, Any]] = app.get_accounts()

    if accounts:
        save_cache(cache)
        return app.acquire_token_silent(scope, account=accounts[0])
    return app.acquire_token_silent(scope, account=None)


def get_exp_date() -> float:
    """Get expiration date for user session

    Returns a float number that represents an expiration date of user session
    The session lifetime is configurable with `ckanext.msal.session_lifetime` option

    Returns:
        Expiration date
    """

    session_ttl = tk.asint(
        tk.config.get(conf.USER_SESSION_TTL, conf.USER_SESSION_TTL_DF)
    )
    return (dt.now() + td(seconds=session_ttl)).timestamp()


def make_password() -> str:
    """Generates a random password.

    Return a random URL-safe text string, in Base64 encoding

    Returns:
        Random password
    """
    return secrets.token_urlsafe(60)


def get_restricted_domains() -> list[str]:
    """Returns a lits of restricted domains from config
    User won't be able to login with this email domain

    Returns:
        A list of restricted domains
    """

    return tk.aslist(tk.config.get(conf.RESTRICTED_DOMAINS), ",")


def get_allowed_domains() -> list[str]:
    """Returns a lits of allowed domains from config
    User will be able to login only with those email domains

    Returns:
        A list of allowed domains
    """

    return tk.aslist(tk.config.get(conf.ALLOWED_DOMAINS), ",")


def is_email_restricted(email: str) -> bool:
    """Check if the user email is restricted by domain.

    Args:
        email (str): user email

    Returns:
        True if restricted
    """

    for domain in get_restricted_domains():
        if email.endswith(domain):
            return True
    return False


def is_email_allowed(email: str) -> bool:
    """Check if the user email is allowed by domain

    Args:
        email (str): user email

    Returns:
        True if allowed
    """

    allowed_domains: list[str] = get_allowed_domains()

    if not allowed_domains:
        return True

    for domain in get_allowed_domains():
        if email.endswith(domain):
            return True
    return False


def get_site_admin_context() -> types.Context:
    site_user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
    return types.Context(user=site_user["name"], ignore_auth=True)


def _clear_session():
    """Wipe out user and its token cache from session"""
    session.clear()


def flash_validation_errors(error: types.ErrorDict) -> None:
    """Adds validation errors to the session flash messages

    Args:
        tk.ValidationError error_dict
    """
    _clear_session()

    session["flash"] = []

    for _, value in error.items():
        session["flash"].append(("alert-error", str(value), True))
