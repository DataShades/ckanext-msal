import logging
from datetime import timedelta

from flask import Blueprint, Response

import ckan.model as model
import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckan.common import session

import ckanext.msal.config as conf
import ckanext.msal.utils as msal_utils
import ckanext.msal.user as user_funcs


log = logging.getLogger(__name__)
msal = Blueprint("msal", __name__)


@msal.route(tk.config.get(conf.REDIRECT_PATH, conf.REDIRECT_PATH_DF))
def authorized() -> Response:
    try:
        cache = msal_utils.load_cache()
        result = msal_utils.build_msal_app(
            cache=cache
        ).acquire_token_by_auth_code_flow(
            session.get("msal_auth_flow", {}), tk.request.args
        )

        session["msal_auth_flow"] = result

        try:
            user_data = user_funcs.get_msal_user_data()
        except tk.ValidationError as e:
            msal_utils.flash_validation_errors(e)
            return h.redirect_to(h.url_for("user.login"))

        if "error" in result or "error" in user_data:
            msal_utils._clear_session()
            log.error(result.get("error") or user_data.get("error"))
            h.flash_error(tk._("Login error. Contact administrator."))
            return h.redirect_to(h.url_for("user.login"))

        session["user"] = user_data
        session["user_exp"] = msal_utils.get_exp_date()
        msal_utils.save_cache(cache)
    except ValueError:
        # Usually caused by CSRF
        # Simply ignore them
        pass

    try:
        user = user_funcs.login_user(session["user"])
    except tk.ValidationError as e:
        msal_utils.flash_validation_errors(e.error_dict)
    else:
        if user := model.User.get(user["id"]):
            tk.login_user(
                user,
                duration=timedelta(
                    milliseconds=tk.asint(
                        tk.config.get(
                            conf.USER_SESSION_TTL, conf.USER_SESSION_TTL_DF
                        )
                    )
                ),
            )
        else:
            log.error(
                "User not found in the database. This should not happen."
            )
            msal_utils._clear_session()

    return h.redirect_to(_destination())


def _destination() -> str:
    """Get the destination URL after login.

    Returns:
        URL to redirect to after login.
    """
    return tk.request.args.get("came_from", "") or tk.config.get(
        "ckan.route_after_login", "dashboard.datasets"
    )


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
