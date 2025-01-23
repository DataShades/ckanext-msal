from datetime import datetime as dt

from ckan.common import session

import ckanext.msal.utils as msal_utils
from ckanext.msal.user import get_msal_user_data, is_user_enabled


def invalidate_user_session() -> None:
    """Invalidate user session if it's expired.

    If user session is expired, clears the session.
    Otherwise, sets a new expiration date.
    """

    if session.get("user"):
        if _is_session_expired():
            if not _is_logged_in():
                msal_utils._clear_session()
            else:
                session["user_exp"] = msal_utils.get_exp_date()


def _is_session_expired() -> bool:
    """Check if user session is expired.

    Returns:
        True if session is expired, False otherwise.
    """

    return dt.now().timestamp() >= session.get("user_exp", 0)


def _is_logged_in() -> bool:
    user_data = get_msal_user_data()
    # TODO: hypothetically, here we can change something in user metadata

    if "error" in user_data or not is_user_enabled(user_data):
        return False

    return True
