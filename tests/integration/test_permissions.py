from typing import Union, Dict, List, Optional

from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.conftest import (
    bypass_api_key_required,
)
from conftest import test_data_creator_flask, monkeysession


def test_permissions(
    test_data_creator_flask: TestDataCreatorFlask,
    bypass_api_key_required,
):
    """
    Test the retrieval, addition, and removal of user permissions
    :param client_with_db:
    :param bypass_api_token_required:
    :return:
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()
    test_user_admin = tdc.get_admin_tus()

    def update_permissions(
        permission: str,
        action: str,
    ):
        tdc.request_validator.update_permissions(
            user_email=tus.user_info.email,
            permission=permission,
            action=action,
            headers=test_user_admin.jwt_authorization_header,
        )

    def get_permissions(expected_json_content: Optional[Union[Dict, List]] = None):
        tdc.request_validator.get_permissions(
            user_email=tus.user_info.email,
            expected_json_content=expected_json_content,
            headers=test_user_admin.jwt_authorization_header,
        )

    get_permissions(expected_json_content=[])
    update_permissions(permission="db_write", action="add")
    get_permissions(expected_json_content=["db_write"])
    update_permissions(permission="db_write", action="remove")
    get_permissions(expected_json_content=[])
