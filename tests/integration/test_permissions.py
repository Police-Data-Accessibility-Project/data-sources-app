from typing import Union, Dict, List, Optional

from psycopg.extras import DictCursor

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from tests.helper_scripts.helper_functions import (
    check_response_status,
    create_test_user_setup,
    run_and_validate_request,
)
from tests.fixtures import (
    flask_client_with_db,
    bypass_api_key_required,
    dev_db_connection,
    test_user_admin,
)


def test_permissions(flask_client_with_db, bypass_api_key_required, test_user_admin):
    """
    Test the retrieval, addition, and removal of user permissions
    :param client_with_db:
    :param bypass_api_token_required:
    :return:
    """

    tus = create_test_user_setup(flask_client_with_db)

    endpoint = f"/auth/permissions?user_email={tus.user_info.email}"

    def run_and_validate_endpoint(
        http_method: str,
        expected_json_content: Optional[Union[Dict, List]] = None,
        **additional_kwargs,
    ):
        run_and_validate_request(
            flask_client=flask_client_with_db,
            http_method=http_method,
            endpoint=endpoint,
            expected_json_content=expected_json_content,
            headers=test_user_admin.jwt_authorization_header,
            **additional_kwargs,
        )

    run_and_validate_endpoint(
        http_method="get",
        expected_json_content=[],
    )

    run_and_validate_endpoint(
        http_method="put",
        json={"action": "add", "permission": "db_write"},
    )

    run_and_validate_endpoint(
        http_method="get",
        expected_json_content=["db_write"],
    )

    run_and_validate_endpoint(
        http_method="put",
        json={"action": "remove", "permission": "db_write"},
    )

    run_and_validate_endpoint(
        http_method="get",
        expected_json_content=[],
    )
