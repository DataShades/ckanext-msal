import msal

import ckan.lib.helpers as h
from ckan.common import session

import ckanext.msal.config as msal_conf


def build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        msal_conf.CLIENT_ID, authority=authority or msal_conf.AUTHORITY,
        client_credential=msal_conf.CLIENT_SECRET, token_cache=cache)


def build_auth_code_flow(authority=None, scopes=None):
    return build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=h.url_for("msal.authorized", _external=True))


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("msal_token_cache"):
        cache.deserialize(session["msal_token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["msal_token_cache"] = cache.serialize()


def _get_token_from_cache(scope=None):
    cache = _load_cache()
    app = build_msal_app(cache=cache)
    accounts = app.get_accounts()
    if accounts:
        _save_cache(cache)
        return app.acquire_token_silent(scope, account=accounts[0])
