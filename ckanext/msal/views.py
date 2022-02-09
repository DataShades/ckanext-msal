import logging
from datetime import datetime as dt

from flask import Blueprint

import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckan.common import session

import ckanext.msal.config as conf
import ckanext.msal.utils as msal_utils
from ckanext.msal.user import get_msal_user_data


log = logging.getLogger(__name__)
msal = Blueprint("msal", __name__)


@msal.route(tk.config.get(conf.REDIRECT_PATH, conf.REDIRECT_PATH_DF))
def authorized():
    try:
        cache = msal_utils._load_cache()
        result = msal_utils.build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("msal_auth_flow", {}), tk.request.args
        )

        session["msal_auth_flow"] = result

        try:
            user_data = get_msal_user_data()
        except tk.ValidationError as e:
            msal_utils._flash_validation_errors(e)
            return h.redirect_to(h.url_for("user.login"))

        if "error" in result or "error" in user_data:
            msal_utils._clear_session()
            log.error(result["error"] or user_data["error"])
            h.flash_error(tk._("Login error. Contact administrator."))
            return h.redirect_to(h.url_for("user.login"))
    
        session["user"] = user_data
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
        msal_utils._clear_session()
        redirect_uri: str = h.url_for("user.logout", _external=True)
        authority: str = tk.config.get(conf.AUTHORITY, conf.AUTHORITY_DF)
        authority_url: str = f"https://login.microsoftonline.com/{authority}"
        return h.redirect_to(
            f"{authority_url}/oauth2/v2.0/logout?post_logout_redirect_uri={redirect_uri}"
        )

    return h.redirect_to("user.logout")


@msal.route("/user/msal-login")
def login():
    flow = msal_utils.build_auth_code_flow(scopes=conf.SCOPE)
    session["msal_auth_flow"] = flow

    return h.redirect_to(flow["auth_uri"], _external=True)


def get_blueprints():
    return [msal]
