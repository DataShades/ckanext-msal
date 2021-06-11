from flask import Blueprint

import ckan.lib.base as base
import ckan.lib.helpers as h
from ckan.common import session, request

import ckanext.msal.config as msal_conf
import ckanext.msal.utils as msal_utils


msal = Blueprint('msal', __name__)


@msal.route(msal_conf.REDIRECT_PATH)
def authorized():
    try:
        cache = msal_utils._load_cache()
        result = msal_utils.build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("msal_auth_flow", {}), request.args)

        if "error" in result:
            h.flash_error(
                "Login error. Contact administrator of your organization.")
            session.clear()
            return h.redirect_to(h.url_for("home"))
        user_data: dict = result.get("id_token_claims")
        session["user"] = result.get("id_token_claims")
        msal_utils._save_cache(cache)
    except ValueError:
        # Usually caused by CSRF
        # Simply ignore them
        pass
    
    return h.redirect_to(h.url_for("dashboard.index"))


@msal.route("/user/msal-logout")
def logout(endpoint="msal_logout"):
    session.clear()  # Wipe out user and its token cache from session
    return h.redirect_to(
        f"{msal_conf.AUTHORITY}/oauth2/v2.0/logout?post_logout_redirect_uri={h.url_for('home', _external=True)}")


@msal.route("/user/msal-login")
def login(endpoint="msal_login"):
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    flow = msal_utils.build_auth_code_flow(scopes=msal_conf.SCOPE)
    session["msal_auth_flow"] = flow

    return h.redirect_to(flow["auth_uri"], _external=True)


def get_blueprints():
    return [msal]
