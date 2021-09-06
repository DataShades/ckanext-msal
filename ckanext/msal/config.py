from ckan.common import config

CLIENT_ID = config.get("ckanext.msal.client_id")
CLIENT_SECRET = config.get("ckanext.msal.client_secret")

AUTHORITY = f"https://login.microsoftonline.com/{config.get('ckanext.msal.tenant_id', 'common')}"
REDIRECT_PATH = config.get("ckanext.msal.redirect_path", "/get_msal_token")

USER_SESSION_LIFETIME = config.get("ckanext.msal.session_lifetime", 3600)

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
# This resource requires no admin consent
# USERS_ENDPOINT = 'https://graph.microsoft.com/v1.0/users'
# USERS_ENDPOINT = 'https://graph.microsoft.com/beta/users/userid?select=identities'
# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]
