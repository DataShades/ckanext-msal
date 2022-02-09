from datetime import datetime as dt

from ckan.common import session

import ckanext.msal.utils as msal_utils
from ckanext.msal.user import get_msal_user_data, is_user_enabled


def _invalidate_user_session():
    """
    Clears session if user session is expired
    Otherwise, sets a new expiration date
    """

    if session.get("user"):
        if _is_session_expired():
            if not is_logged_in():
                msal_utils._clear_session()
            else:
                session["user_exp"] = msal_utils._get_exp_date()


def _is_session_expired() -> bool:
    """
    Returns `True` if user session is expired

    return
    type: bool
    """

    if dt.now().timestamp() >= session.get("user_exp", 0):
        return True
    return False


def is_logged_in():
    user_data = get_msal_user_data()
    # TODO: hypothetically, here we can change something in user metadata

    if "error" in user_data or not is_user_enabled(user_data):
        return False

    return True


class SessionInvalidator(object):
    def __init__(self, app):
        """Initialize the Session Invalidator Middleware"""
        self.app = app
        app.before_request(_invalidate_user_session)

    def __call__(self, environ, start_response):

        return self.app(environ, start_response)
