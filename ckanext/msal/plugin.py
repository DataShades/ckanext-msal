import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckan.model as model
from ckan.common import session

from ckanext.msal.middleware import SessionInvalidator
from ckanext.msal.views import get_blueprints
import ckanext.msal.user as user_funcs


class MsalPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IAuthenticator, inherit=True)
    p.implements(p.IMiddleware, inherit=True)
    p.implements(p.IBlueprint, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, 'templates')
        tk.add_public_directory(config_, 'public')
        tk.add_resource('fanstatic', 'msal')

    # IMiddleware
    def make_middleware(self, app, config):
        return SessionInvalidator(app)

    # IBlueprint
    def get_blueprint(self):
        return get_blueprints()

    # IAuthenticator
    def identify(self):
        u'''Called to identify the user.

        If the user is identified then it should set:

         - tk.g.user: The name of the user
         - tk.g.userobj: The actual user object
        '''

        if session.get('user') and not any((tk.g.setdefault('userobj'), tk.g.setdefault('user'))):
            user = user_funcs._login_user(session['user'])

            if user:
                tk.g.user = user["name"]
    
    def logout(self):
        session.clear()