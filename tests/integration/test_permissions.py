from tests.helper_scripts.helper_functions import (
    check_response_status,
    create_test_user_setup,
)
from tests.fixtures import flask_client_with_db, bypass_api_token_required, dev_db_connection


def test_permissions(flask_client_with_db, bypass_api_token_required):
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
        headers=tus.authorization_header,
    )
    check_response_status(response, 200)
    assert response.json == []

    response = flask_client_with_db.put(
        endpoint,
        json={"action": "add", "permission": "db_write"},
        headers=tus.authorization_header,
    )
    check_response_status(response, 200)

    response = flask_client_with_db.get(
        endpoint,
        headers=tus.authorization_header,
    )
    check_response_status(response, 200)
    assert response.json == ["db_write"]

    response = flask_client_with_db.put(
        endpoint,
        json={"action": "remove", "permission": "db_write"},
        headers=tus.authorization_header,
    )
    check_response_status(response, 200)

    response = flask_client_with_db.get(
        endpoint,
        headers=tus.authorization_header,
    )
    check_response_status(response, 200)
    assert response.json == []
