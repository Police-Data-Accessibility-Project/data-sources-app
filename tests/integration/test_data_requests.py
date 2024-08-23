import uuid
from http import HTTPStatus

import psycopg2

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from tests.fixtures import (
    connection_with_test_data,
    flask_client_with_db,
    db_client_with_test_data,
    test_user_admin,
    dev_db_client,
    dev_db_connection,
)
from tests.helper_scripts.helper_functions import (
    create_test_user_setup,
    run_and_validate_request,
    create_test_user_setup_db_client,
)


GENERAL_ENDPOINT = "/api/data-requests/"
BY_ID_ENDPOINT = GENERAL_ENDPOINT + "by-id/"


def test_data_requests_get(flask_client_with_db, dev_db_client):
    tus = create_test_user_setup(flask_client_with_db)

    submission_notes = str(uuid.uuid4())

    data_request_id_creator = dev_db_client.create_data_request({
        "submission_notes": submission_notes,
        "creator_user_id": tus.user_info.user_id
    })


    json_data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=GENERAL_ENDPOINT,
        headers=tus.jwt_authorization_header,
    )
    assert len(json_data["data_requests"]) > 0
    assert isinstance(json_data["data_requests"], list)
    assert isinstance(json_data["data_requests"][0], dict)

    # Check that first result is user's data request
    assert json_data["data_requests"][0]["id"] == data_request_id_creator

    # Check that last result is not user's data request
    assert json_data["data_requests"][-1]["id"] != data_request_id_creator

    # Give user admin permission
    dev_db_client.add_user_permission(
        user_email=tus.user_info.email,
        permission=PermissionsEnum.DB_WRITE
    )

    admin_json_data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=GENERAL_ENDPOINT,
        headers=tus.jwt_authorization_header,
    )

    # Assert admin columns are greater than user columns
    assert len(admin_json_data["data_requests"][0]) > len(json_data["data_requests"][0])


def test_data_requests_post(flask_client_with_db, dev_db_client):

    tus = create_test_user_setup(flask_client_with_db)

    submission_notes = str(uuid.uuid4())

    json_data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint=GENERAL_ENDPOINT,
        headers=tus.jwt_authorization_header,
        json={"entry_data": {"submission_notes": submission_notes}},
    )

    data_request_id = json_data["data_request_id"]
    user_id = dev_db_client.get_user_id(tus.user_info.email)
    results = dev_db_client.get_data_requests(
        columns=["id", "submission_notes", "creator_user_id"],
        where_mappings={"id": data_request_id},
    )

    assert len(results) == 1
    assert results[0][1] == submission_notes
    assert results[0][2] == user_id

    # Check that response is forbidden for standard user
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint=GENERAL_ENDPOINT,
        headers=tus.api_authorization_header,
        json={"entry_data": {"submission_notes": submission_notes}},
        expected_response_status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    # Check that response is forbidden if using invalid columns
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint=GENERAL_ENDPOINT,
        headers=tus.jwt_authorization_header,
        json={"entry_data": {"id": 1}},
        expected_response_status=HTTPStatus.FORBIDDEN,
    )


def test_data_requests_by_id_get(flask_client_with_db, dev_db_client):
    tus = create_test_user_setup(
        flask_client_with_db,
        permissions=[PermissionsEnum.DB_WRITE],
    )

    submission_notes = str(uuid.uuid4())
    data_request_id = dev_db_client.create_data_request(
        data_request_info={
            "submission_notes": submission_notes,
        }
    )

    api_json_data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=tus.api_authorization_header,
    )

    assert api_json_data["data_request"]["submission_notes"] == submission_notes

    jwt_json_data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=tus.jwt_authorization_header,
    )

    assert jwt_json_data["data_request"]["submission_notes"] == submission_notes

    #  Confirm elevated user has more columns than standard user
    assert len(jwt_json_data["data_request"].keys()) > len(
        api_json_data["data_request"].keys()
    )


def test_data_requests_by_id_put(flask_client_with_db, dev_db_client):
    tus = create_test_user_setup(flask_client_with_db)

    submission_notes = str(uuid.uuid4())
    data_request_id = dev_db_client.create_data_request(
        data_request_info={
            "submission_notes": submission_notes,
            "creator_user_id": tus.user_info.user_id,
        }
    )

    result = dev_db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings={"id": data_request_id},
    )

    assert result[0][0] == submission_notes

    new_submission_notes = str(uuid.uuid4())

    json_data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="put",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=tus.jwt_authorization_header,
        json={"entry_data": {"submission_notes": new_submission_notes}},
    )

    result = dev_db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings={"id": data_request_id},
    )

    assert result[0][0] == new_submission_notes

    # Check that request is denied on admin-only column
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="put",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=tus.jwt_authorization_header,
        json={"entry_data": {"request_status": "approved"}},
        expected_response_status=HTTPStatus.FORBIDDEN,
    )



def test_data_requests_by_id_delete(flask_client_with_db, dev_db_client):
    tus = create_test_user_setup(
        flask_client_with_db, permissions=[PermissionsEnum.DB_WRITE]
    )

    submission_notes = str(uuid.uuid4())
    data_request_id = dev_db_client.create_data_request(
        data_request_info={
            "submission_notes": submission_notes,
            "creator_user_id": tus.user_info.user_id,
        }
    )

    json_data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="delete",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=tus.jwt_authorization_header,
    )

    result = dev_db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings={"id": data_request_id},
    )

    assert result == []

    # Check that request is denied if user does not have DB_WRITE permission
    tus_2 = create_test_user_setup(flask_client_with_db)

    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="delete",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=tus_2.jwt_authorization_header,
        expected_response_status=HTTPStatus.FORBIDDEN,
    )

    # But if user is owner, allow
    new_data_request_id = dev_db_client.create_data_request(
        data_request_info={
            "submission_notes": submission_notes,
            "creator_user_id": tus_2.user_info.user_id,
        }
    )

    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="delete",
        endpoint=BY_ID_ENDPOINT + str(new_data_request_id),
        headers=tus_2.jwt_authorization_header,
    )

