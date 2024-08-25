import uuid
from collections import namedtuple
from http import HTTPStatus

import pytest

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
)


GENERAL_ENDPOINT = "/api/data-requests/"
BY_ID_ENDPOINT = GENERAL_ENDPOINT + "by-id/"

TestSetup = namedtuple(
    "TestSetup",
    [
        "flask_client",
        "db_client",
        "submission_notes",
        "tus"
    ])

@pytest.fixture
def ts(flask_client_with_db, dev_db_client):
    return TestSetup(
        flask_client=flask_client_with_db,
        db_client=dev_db_client,
        submission_notes=str(uuid.uuid4().hex),
        tus = create_test_user_setup(flask_client_with_db)
    )




def test_data_requests_get(ts: TestSetup):

    data_request_id_not_creator = create_data_request(ts.db_client, ts.submission_notes)
    data_request_id_creator = create_data_request(ts.db_client, ts.submission_notes, ts.tus.user_info.user_id)

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=GENERAL_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
    )
    assert len(json_data["data_requests"]) > 0
    assert isinstance(json_data["data_requests"], list)
    assert isinstance(json_data["data_requests"][0], dict)

    # Check that first result is user's data request
    assert json_data["data_requests"][0]["id"] == data_request_id_creator

    # Check that last result is not user's data request
    assert json_data["data_requests"][-1]["id"] != data_request_id_creator

    # Give user admin permission
    ts.db_client.add_user_permission(
        user_email=ts.tus.user_info.email,
        permission=PermissionsEnum.DB_WRITE
    )

    admin_json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=GENERAL_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
    )

    # Assert admin columns are greater than user columns
    assert len(admin_json_data["data_requests"][0]) > len(json_data["data_requests"][0])


def create_data_request(dev_db_client, submission_notes, user_id = None):
    data_request_id_creator = dev_db_client.create_data_request({
        "submission_notes": submission_notes,
        "creator_user_id": user_id
    })
    return data_request_id_creator


def test_data_requests_post(ts: TestSetup):


    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=GENERAL_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"submission_notes": ts.submission_notes}},
    )

    data_request_id = json_data["data_request_id"]
    user_id = ts.db_client.get_user_id(ts.tus.user_info.email)
    results = ts.db_client.get_data_requests(
        columns=["id", "submission_notes", "creator_user_id"],
        where_mappings={"id": data_request_id},
    )

    assert len(results) == 1
    assert results[0]["submission_notes"] == ts.submission_notes
    assert results[0]["creator_user_id"] == user_id

    # Check that response is forbidden for standard user
    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=GENERAL_ENDPOINT,
        headers=ts.tus.api_authorization_header,
        json={"entry_data": {"submission_notes": ts.submission_notes}},
        expected_response_status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    # Check that response is forbidden if using invalid columns
    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=GENERAL_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"id": 1}},
        expected_response_status=HTTPStatus.FORBIDDEN,
    )


def test_data_requests_by_id_get(ts: TestSetup):
    ts.db_client.add_user_permission(
        ts.tus.user_info.email,
        PermissionsEnum.DB_WRITE
    )

    data_request_id = create_data_request(ts.db_client, ts.submission_notes)

    api_json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=ts.tus.api_authorization_header,
    )

    assert api_json_data["data_request"]["submission_notes"] == ts.submission_notes

    jwt_json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=ts.tus.jwt_authorization_header,
    )

    assert jwt_json_data["data_request"]["submission_notes"] == ts.submission_notes

    #  Confirm elevated user has more columns than standard user
    assert len(jwt_json_data["data_request"].keys()) > len(
        api_json_data["data_request"].keys()
    )


def test_data_requests_by_id_put(ts: TestSetup):

    data_request_id = create_data_request(ts.db_client, ts.submission_notes, ts.tus.user_info.user_id)

    result = ts.db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings={"id": data_request_id},
    )

    assert result[0]["submission_notes"] == ts.submission_notes

    new_submission_notes = str(uuid.uuid4())

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="put",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"submission_notes": new_submission_notes}},
    )

    result = ts.db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings={"id": data_request_id},
    )

    assert result[0]["submission_notes"] == new_submission_notes

    # Check that request is denied on admin-only column
    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="put",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"request_status": "approved"}},
        expected_response_status=HTTPStatus.FORBIDDEN,
    )



def test_data_requests_by_id_delete(ts: TestSetup):
    ts.db_client.add_user_permission(
        ts.tus.user_info.email,
        PermissionsEnum.DB_WRITE
    )

    data_request_id = create_data_request(ts.db_client, ts.submission_notes, ts.tus.user_info.user_id)

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="delete",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=ts.tus.jwt_authorization_header,
    )

    result = ts.db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings={"id": data_request_id},
    )

    assert result == []

    # Check that request is denied if user does not have DB_WRITE permission
    tus_2 = create_test_user_setup(ts.flask_client)

    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="delete",
        endpoint=BY_ID_ENDPOINT + str(data_request_id),
        headers=tus_2.jwt_authorization_header,
        expected_response_status=HTTPStatus.FORBIDDEN,
    )

    # But if user is owner, allow
    new_data_request_id = create_data_request(ts.db_client, ts.submission_notes, tus_2.user_info.user_id)

    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="delete",
        endpoint=BY_ID_ENDPOINT + str(new_data_request_id),
        headers=tus_2.jwt_authorization_header,
    )

