from ckan.common import config

CLIENT_ID = config.get("ckanext.msal.client_id")
CLIENT_SECRET = config.get("ckanext.msal.client_secret")
AUTHORITY = f"https://login.microsoftonline.com/{config.get('ckanext.msal.tenant_id', 'common')}"
REDIRECT_PATH = config.get("ckanext.msal.redirect_path", "/get_msal_token")
USER_SESSION_LIFETIME = config.get("ckanext.msal.session_lifetime", 3600)

SCOPE = ["User.ReadBasic.All"]
