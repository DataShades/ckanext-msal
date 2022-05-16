import ckan.plugins.toolkit as tk
from ckan.common import config


CLIENT_ID = "ckanext.msal.client_id"
CLIENT_SECRET = "ckanext.msal.client_secret"
AUTHORITY = "ckanext.msal.tenant_id"
AUTHORITY_DF = "common"
REDIRECT_PATH = "ckanext.msal.redirect_path"
REDIRECT_PATH_DF = "/get_msal_token"
USER_SESSION_TTL = "ckanext.msal.session_lifetime"
USER_SESSION_TTL_DF = 3600
RESTRICTED_DOMAINS = "ckanext.msal.restrict.restricted_domain_list"
ALLOWED_DOMAINS = "ckanext.msal.restrict.allowed_domain_list"
RESTRICTION_ERR = "ckanext.msal.restrict.error_message"
RESTRICTION_ERR_DF = "Your email domain is restricted. Please, contact site admin."

EMAIL_CASE_INSENSITIVE = "ckanext.msal.email_case_insensitive"
EMAIL_CASE_INSENSITIVE_DF = False

MERGE_MATCHING_EMAILS = "ckanext.msal.merge_matching_emails"
MERGE_MATCHING_EMAILS_DF = False

SCOPE = ["User.ReadBasic.All"]
