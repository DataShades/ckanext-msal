from ckan.common import config


CLIENT_ID = config.get("ckanext.msal.client_id")
CLIENT_SECRET = config.get("ckanext.msal.client_secret")

AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
REDIRECT_PATH = config.get("ckanext.msal.redirect_path", "/get_msal_token")

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
# This resource requires no admin consent
USERS_ENDPOINT = 'https://graph.microsoft.com/beta/users'

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]
