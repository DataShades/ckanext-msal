import logging
from datetime import datetime as dt

from flask import Blueprint

import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckan.common import session, request

import ckanext.msal.config as msal_conf
import ckanext.msal.utils as msal_utils
from ckanext.msal.user import get_msal_user_data


log = logging.getLogger(__name__)
msal = Blueprint("msal", __name__)


@msal.route(msal_conf.REDIRECT_PATH)
def authorized():
    try:
        cache = msal_utils._load_cache()
        result = msal_utils.build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("msal_auth_flow", {}), request.args
        )

        if "error" in result:
            session.clear()
            log.error(result["error"])
            h.flash_error(tk._("Login error. Contact administrator."))
            return h.redirect_to(h.url_for("user.login"))

        session["user"] = get_msal_user_data()
        session["user_exp"] = msal_utils._get_exp_date()
        msal_utils._save_cache(cache)
    except ValueError:
        # Usually caused by CSRF
        # Simply ignore them
        pass

    return h.redirect_to(h.url_for("dashboard.index"))


@msal.route("/user/msal-logout")
def logout():
    if session.get("msal_auth_flow") or session.get("msal_token_cache"):
        session.clear()  # Wipe out user and its token cache from session
        redirect_uri: str = h.url_for("user.logout", _external=True)
        return h.redirect_to(
            f"{msal_conf.AUTHORITY}/oauth2/v2.0/logout?post_logout_redirect_uri={redirect_uri}"
        )

    return h.redirect_to("user.logout")


@msal.route("/user/msal-login")
def login():
    flow = msal_utils.build_auth_code_flow(scopes=msal_conf.SCOPE)
    session["msal_auth_flow"] = flow

    return h.redirect_to(flow["auth_uri"], _external=True)


def get_blueprints():
    return [msal]
