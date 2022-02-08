from datetime import datetime as dt

import pytest

import ckanext.msal.utils as utils


@pytest.mark.ckan_config("ckan.plugins", "msal")
@pytest.mark.usefixtures("with_plugins")
class TestUtils(object):
    user_dict = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
        "@odata.id": "https://graph.microsoft.com/v2/3c8827a9-65fe-40b5-8644-3173d7026601/directoryObjects/fb9c93ba-0768-4816-8fcc-802b588fb8bf/Microsoft.DirectoryServices.User",
        "businessPhones": ["380666333211"],
        "displayName": "Mark Spencer",
        "givenName": "Mark",
        "mailNickname": "mark209",
        "jobTitle": None,
        "mail": None,
        "mobilePhone": None,
        "officeLocation": None,
        "preferredLanguage": None,
        "surname": "Spencer",
        "userPrincipalName": "kvaqich@kvaqich.onmicrosoft.com",
        "id": "fb9c93ba-0768-4816-8fcc-802b588fb8bf",
    }

    def test_exp_date(self):
        exp_date: float = utils._get_exp_date()

        assert isinstance(exp_date, float)
        assert dt.now().timestamp() < exp_date

    def test_make_password(self):
        pass1 = utils._make_password()
        pass2 = utils._make_password()

        assert len(pass1) > 16
        assert pass1 != pass2
