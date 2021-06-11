from datetime import datetime as dt

from ckan.common import session


def _invalidate_user_session():
    print(session.get('user'))
    if user_data := session.get('user'):
        if dt.now().timestamp() >= user_data['exp']:
            session.clear()


class SessionInvalidator(object):
    def __init__(self, app):
        """Initialize the Session Invalidator Middleware

        ``config``
            dict  All settings should be prefixed by 'ckanext.msal.'.
        """
        self.app = app
        app.before_request(_invalidate_user_session)

    def __call__(self, environ, start_response):

        return self.app(environ, start_response)
