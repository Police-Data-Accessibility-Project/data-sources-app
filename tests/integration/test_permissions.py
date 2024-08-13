from psycopg2.extras import DictCursor

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from tests.helper_scripts.helper_functions import (
    check_response_status,
    create_test_user_setup,
)
from tests.fixtures import flask_client_with_db, bypass_api_key_required, dev_db_connection, test_user_admin


def test_permissions(flask_client_with_db, bypass_api_key_required, test_user_admin):
    """
    Test the retrieval, addition, and removal of user permissions
    :param client_with_db:
    :param bypass_api_token_required:
    :return:
    """

    tus = create_test_user_setup(flask_client_with_db)

    endpoint = f"/auth/permissions?user_email={tus.user_info.email}"

    response = flask_client_with_db.get(
        endpoint,
        headers=test_user_admin.jwt_authorization_header,
    )
    check_response_status(response, 200)
    assert response.json == []

    response = flask_client_with_db.put(
        endpoint,
        json={"action": "add", "permission": "db_write"},
        headers=test_user_admin.jwt_authorization_header,
    )
    check_response_status(response, 200)

    response = flask_client_with_db.get(
        endpoint,
        headers=test_user_admin.jwt_authorization_header,
    )
    check_response_status(response, 200)
    assert response.json == ["db_write"]

    response = flask_client_with_db.put(
        endpoint,
        json={"action": "remove", "permission": "db_write"},
        headers=test_user_admin.jwt_authorization_header,
    )
    check_response_status(response, 200)

    response = flask_client_with_db.get(
        endpoint,
        headers=test_user_admin.jwt_authorization_header,
    )
    check_response_status(response, 200)
    assert response.json == []
