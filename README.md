# ckanext-msal

This extension allows you to sign in users with Microsoft identities (Azure AD, Microsoft Accounts and Azure AD B2C accounts). It uses [Microsoft MSAL](https://github.com/AzureAD/microsoft-authentication-library-for-python) library.

It works with Microsoft 365 accounts. But in future, the situation could change.

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.7 and earlier | no            |
| 2.8             | no            |
| 2.9             | no            |
| 2.10.0+         | yes           |

## Installation

To install ckanext-msal:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/DataShades/ckanext-msal.git
    cd ckanext-msal
    pip install -e .
	pip install -r requirements.txt

3. Add `msal` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings
	# The application client id. Mandatory option.
	ckanext.msal.client_id = 000000-0000-0000-0000-00000000000

	# The client secret. Mandatory option.
	ckanext.msal.client_secret = 000000-0000-0000-0000-00000000000

    # The tenant ID. If it's not provided, the common one for multi-tenant app will be used.
    # In this case, the application is not guaranteed to work properly.
    # (optional, default: 'common').
    ckanext.msal.tenant_id = 000000-0000-0000-0000-00000000000

    # The redirect path should be setted up in Azure AD web app config.
    # It handles the response from Microsoft.
    # (optional, default: "/get_msal_token").
    ckanext.msal.redirect_path

    # While the session lifespan could be manage only in Azure AD conditional policies panel,
    # this option actually implies how often do we send a test request for the Microsoft Graph API
    # to check if our Access token is still alive.
    # (optional, default: 3600, in seconds).
    ckanext.msal.session_lifetime = 3600

    # The list of restricted email domains. User won't be able to login under
    # an email with those domains (optional, default: None)
    ckanext.msal.restrict.domain_list = gmail.com, onmicrosoft.com

    # The list of allowed email domains. User won't be able to login under
    # any other emails (optional, default: None)
    ckanext.msal.restrict.allowed_domain_list = protonmail.com, orgname.onmicrosoft.com

    # A message that will be shown to users with a restricted domain
    # (optional, default: "Your email domain is restricted. Please, contact site admin.")
    ckanext.msal.restrict.error_message

## Developer installation

To install ckanext-msal for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/DataShades/ckanext-msal.git
    cd ckanext-msal
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

If you changed something - be sure to run tests before merging your changes. To run tests, do:

    pytest --ckan-ini=test.ini


## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
