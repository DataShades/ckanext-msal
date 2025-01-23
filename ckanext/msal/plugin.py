import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.msal.middleware import invalidate_user_session
from ckanext.msal.views import get_blueprints
import ckanext.msal.utils as utils


class MsalPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IAuthenticator, inherit=True)
    p.implements(p.IMiddleware, inherit=True)
    p.implements(p.IBlueprint, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")

    # IMiddleware

    def make_middleware(self, app, config):
        app.before_request(invalidate_user_session)
        return app

    # IBlueprint

    def get_blueprint(self):
        return get_blueprints()

    # IAuthenticator

    def logout(self):
        utils._clear_session()
