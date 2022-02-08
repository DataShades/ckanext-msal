from datetime import datetime as dt

import pytest

from ckan.tests import factories
import ckanext.msal.user as user_funcs


@pytest.mark.ckan_config("ckan.plugins", "msal")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestUser(object):
    user_dict = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
        "@odata.id": "https://graph.microsoft.com/v2/3c8827a9-65fe-40b5-8644-3173d7026601/directoryObjects/fb9c93ba-0768-4816-8fcc-802b588fb8bf/Microsoft.DirectoryServices.User",
        "businessPhones": ["380999222611"],
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

    def test_get_email_upn(self):
        """
        Returns userPrincipalName from user_dict
        """
        email = user_funcs._get_email(self.user_dict)
        assert email == "kvaqich@kvaqich.onmicrosoft.com"

    def test_get_email_mail(self):
        """
        Returns `mail` field if `userPrincipalName` is empty
        """
        email = user_funcs._get_email({"mail": "kvaqich@kvaqich.onmicrosoft.com"})
        assert email == "kvaqich@kvaqich.onmicrosoft.com"

    def test_get_email_empty(self):
        """
        Returns random email if both fields are empty
        """
        email = user_funcs._get_email({})
        assert email
        assert email.endswith("msal.onmicrosoft.com")

    def test_get_username(self):
        """
        Fetches username from user_dict
        mailNickname -> munge(mail) -> munge(userPrincipalName)
        """
        username = user_funcs._get_username(self.user_dict)
        username == "mark209"

        username = user_funcs._get_username({"mail": "testuser@gmail.com"})
        username == "testuser"

        username = user_funcs._get_username(
            {"userPrincipalName": "testuser2@gmail.com"}
        )
        username == "testuser2"

    def test_is_username_unqiue(self):
        user = factories.User()

        is_unique: bool = user_funcs._is_username_unique(user["name"])
        assert not is_unique

        is_unique: bool = user_funcs._is_username_unique("absolutely_new_user")
        assert is_unique
