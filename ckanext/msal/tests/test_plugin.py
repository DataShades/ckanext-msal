import pytest
import mock

from ckan.common import config, session

import ckanext.msal.plugin as plugin
from ckanext.msal.user import _login_user


@pytest.mark.ckan_config("ckan.plugins", "msal")
@pytest.mark.usefixtures("with_plugins", "with_request_context")
def test_login(app):
    user = {
        "aud": "45f7852c-628c-437f-b3f2-2df26976b1e5",
        "iss": "https://login.microsoftonline.com/3c8827a9-65fe-40b5-8644-3173d7026601/v2.0",
        "iat": 1630936420,
        "nbf": 1630936420,
        "exp": 1630940320,
        "name": "Mark Spencer",
        "nonce": "a8d30f17e256f8d5ae042cca2087e8a848871d080ad4349248fce49c558ba7cb",
        "oid": "fb9c93ba-0768-4816-8fcc-802b588fb8bf",
        "preferred_username": "kvaqich@kvaqich.onmicrosoft.com",
        "rh": "0.AQwAqSeIPP5ltUCGRDFz1wJmASyF90WMYn9Ds_It8ml2seUMAHo.",
        "sub": "uXUZ-tk_v6B1Ix82gyQhyPp8CR_CLu5MUVmtkq4Y0To",
        "tid": "3c8827a9-65fe-40b5-8644-3173d7026601",
        "uti": "acThZD9K4EaUOYdVYkxaAA",
        "ver": "2.0",
    }
    with mock.patch(
        "ckanext.msal.user.get_msal_user_data",
        return_value={
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
            "surname": "Pavlyuk",
            "userPrincipalName": "kvaqich@kvaqich.onmicrosoft.com",
            "id": "fb9c93ba-0768-4816-8fcc-802b588fb8bf",
        },
    ) as get_msal_user_data:
        user_data = _login_user(user)
        assert user["oid"] == user_data["id"]
