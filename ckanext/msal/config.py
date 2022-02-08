import ckan.plugins.toolkit as tk
from ckan.common import config


CLIENT_ID = config.get("ckanext.msal.client_id")
CLIENT_SECRET = config.get("ckanext.msal.client_secret")
AUTHORITY = f"https://login.microsoftonline.com/{config.get('ckanext.msal.tenant_id', 'common')}"
REDIRECT_PATH = config.get("ckanext.msal.redirect_path", "/get_msal_token")
USER_SESSION_LIFETIME = config.get("ckanext.msal.session_lifetime", 3600)
RESTRICTED_DOMAINS = config.get("ckanext.msal.restrict.restricted_domain_list")
ALLOWED_DOMAINS = config.get("ckanext.msal.restrict.allowed_domain_list")
RESTRICTION_ERR = config.get(
    "ckanext.msal.restrict.error_message",
    "Your email domain is restricted. Please, contact site admin.",
)
MERGE_MATCHING_EMAILS = tk.asbool(
    config.get("ckanext.msal.merge_matching_emails", False)
)

SCOPE = ["User.ReadBasic.All"]
