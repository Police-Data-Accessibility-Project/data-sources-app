import uuid
from collections import namedtuple
from dataclasses import dataclass
from http import HTTPStatus
from typing import Dict, Optional

import pytest
from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from middleware.constants import DATA_KEY
from middleware.enums import PermissionsEnum
from tests.fixtures import (
    flask_client_with_db,
    dev_db_client,
)
from tests.helper_scripts.common_endpoint_calls import create_data_source_with_endpoint
from tests.helper_scripts.constants import (
    DATA_REQUESTS_BASE_ENDPOINT,
    DATA_REQUESTS_BY_ID_ENDPOINT,
    DATA_REQUESTS_GET_RELATED_SOURCE_ENDPOINT,
    DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT,
)
from tests.helper_scripts.helper_classes.IntegrationTestSetup import (
    integration_test_setup,
)
from tests.helper_scripts.helper_functions import (
    create_test_user_setup,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.helper_classes.IntegrationTestSetup import (
    IntegrationTestSetup,
)


@dataclass
class DataRequestsTestSetup(IntegrationTestSetup):
    submission_notes: str = str(uuid.uuid4())


@pytest.fixture
def ts(flask_client_with_db, dev_db_client):
    return DataRequestsTestSetup(
        flask_client=flask_client_with_db,
        db_client=dev_db_client,
        tus=create_test_user_setup(flask_client_with_db),
    )


def test_data_requests_get(ts: DataRequestsTestSetup):

    tus_not_creator = create_test_user_setup(ts.flask_client)
    create_data_request_with_endpoint(
        flask_client=ts.flask_client,
        jwt_authorization_header=tus_not_creator.jwt_authorization_header,
    )
    cdr = create_data_request_with_endpoint(
        flask_client=ts.flask_client,
        jwt_authorization_header=ts.tus.jwt_authorization_header,
    )
    data_request_id_creator = int(cdr.id)

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
    )
    assert len(json_data[DATA_KEY]) > 0
    assert isinstance(json_data[DATA_KEY], list)
    assert isinstance(json_data[DATA_KEY][0], dict)

    # Check that first result is user's data request
    assert json_data[DATA_KEY][0]["id"] == data_request_id_creator

    # Check that last result is not user's data request
    assert json_data[DATA_KEY][-1]["id"] != data_request_id_creator

    # Give user admin permission
    ts.db_client.add_user_permission(
        user_email=ts.tus.user_info.email, permission=PermissionsEnum.DB_WRITE
    )

    admin_json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
    )

    # Assert admin columns are greater than user columns
    assert len(admin_json_data[DATA_KEY][0]) > len(json_data[DATA_KEY][0])


def create_data_request(dev_db_client, submission_notes, user_id=None):
    data_request_id_creator = dev_db_client.create_data_request(
        column_value_mappings={
            "submission_notes": submission_notes,
            "creator_user_id": user_id,
        }
    )
    return data_request_id_creator


CreatedDataRequest = namedtuple("CreatedDataRequest", ["id", "submission_notes"])


def create_data_request_with_endpoint(
    flask_client: FlaskClient,
    jwt_authorization_header: dict,
) -> CreatedDataRequest:
    """
    Create a data request via an API call
    :param flask_client:
    :param jwt_authorization_header:
    :return:
    """
    submission_notes = uuid.uuid4().hex

    json = run_and_validate_request(
        flask_client=flask_client,
        http_method="post",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=jwt_authorization_header,
        json={"entry_data": {"submission_notes": submission_notes}},
    )

    cdr = CreatedDataRequest(id=json["id"], submission_notes=submission_notes)
    return cdr


def test_data_requests_post(ts: DataRequestsTestSetup):

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"submission_notes": ts.submission_notes}},
    )

    data_request_id = json_data["id"]
    user_id = ts.db_client.get_user_id(ts.tus.user_info.email)
    results = ts.db_client.get_data_requests(
        columns=[
            "id",
            "submission_notes",
            "creator_user_id",
        ],
        where_mappings=[WhereMapping(column="id", value=int(data_request_id))],
    )

    assert len(results) == 1
    assert results[0]["submission_notes"] == ts.submission_notes
    assert results[0]["creator_user_id"] == user_id

    # Check that response is forbidden for standard user
    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=ts.tus.api_authorization_header,
        json={"entry_data": {"submission_notes": ts.submission_notes}},
        expected_response_status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    # Check that response is forbidden if using invalid columns
    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"id": 1}},
        expected_response_status=HTTPStatus.FORBIDDEN,
    )


def test_data_requests_by_id_get(ts: DataRequestsTestSetup):
    ts.db_client.add_user_permission(ts.tus.user_info.email, PermissionsEnum.DB_WRITE)

    data_request_id = create_data_request(ts.db_client, ts.submission_notes)

    api_json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT + str(data_request_id),
        headers=ts.tus.api_authorization_header,
    )

    assert api_json_data[DATA_KEY]["submission_notes"] == ts.submission_notes

    jwt_json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT + str(data_request_id),
        headers=ts.tus.jwt_authorization_header,
    )

    assert jwt_json_data[DATA_KEY]["submission_notes"] == ts.submission_notes

    #  Confirm elevated user has more columns than standard user
    assert len(jwt_json_data[DATA_KEY].keys()) > len(api_json_data[DATA_KEY].keys())


def test_data_requests_by_id_put(ts: DataRequestsTestSetup):

    data_request_id = create_data_request(
        ts.db_client, ts.submission_notes, ts.tus.user_info.user_id
    )

    result = ts.db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings=[WhereMapping(column="id", value=data_request_id)],
    )

    assert result[0]["submission_notes"] == ts.submission_notes

    new_submission_notes = str(uuid.uuid4())

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="put",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT + str(data_request_id),
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"submission_notes": new_submission_notes}},
    )

    result = ts.db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings=[WhereMapping(column="id", value=data_request_id)],
    )

    assert result[0]["submission_notes"] == new_submission_notes

    # Check that request is denied on admin-only column
    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="put",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT + str(data_request_id),
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"request_status": "approved"}},
        expected_response_status=HTTPStatus.FORBIDDEN,
    )


def test_data_requests_by_id_delete(ts: DataRequestsTestSetup):

    ts.db_client.add_user_permission(ts.tus.user_info.email, PermissionsEnum.DB_WRITE)

    tus_admin = ts.tus
    tus_owner = create_test_user_setup(ts.flask_client)
    tus_non_owner = create_test_user_setup(ts.flask_client)

    data_request_id = create_data_request(
        ts.db_client, ts.submission_notes, tus_owner.user_info.user_id
    )

    # Owner should be able to delete their own request
    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="delete",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT + str(data_request_id),
        headers=tus_owner.jwt_authorization_header,
    )

    assert (
        ts.db_client.get_data_requests(
            columns=["submission_notes"],
            where_mappings=[WhereMapping(column="id", value=data_request_id)],
        )
        == []
    )

    # Check that request is denied if user is not owner and does not have DB_WRITE permission
    new_data_request_id = create_data_request(
        ts.db_client, ts.submission_notes, tus_owner.user_info.user_id
    )

    NEW_ENDPOINT = DATA_REQUESTS_BY_ID_ENDPOINT + str(new_data_request_id)

    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="delete",
        endpoint=NEW_ENDPOINT,
        headers=tus_non_owner.jwt_authorization_header,
        expected_response_status=HTTPStatus.FORBIDDEN,
    )

    # But if user is an admin, allow
    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="delete",
        endpoint=NEW_ENDPOINT,
        headers=tus_admin.jwt_authorization_header,
    )

    # If data request id doesn't exist (or is already deleted), return 404
    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="delete",
        endpoint=NEW_ENDPOINT,
        headers=tus_admin.jwt_authorization_header,
        expected_response_status=HTTPStatus.NOT_FOUND,
    )


def get_data_request_related_sources_with_endpoint(
    flask_client: FlaskClient,
    api_authorization_header: Dict[str, str],
    data_request_id: int,
    expected_json_content: Optional[dict],
):
    return run_and_validate_request(
        flask_client=flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_GET_RELATED_SOURCE_ENDPOINT.format(
            data_request_id=data_request_id
        ),
        headers=api_authorization_header,
        expected_json_content=expected_json_content,
    )


class DataRequestByRelatedSourcesTestSetup(IntegrationTestSetup):

    def __init__(
        self,
        flask_client: FlaskClient,
        db_client: DatabaseClient,
    ):
        self.flask_client = flask_client
        self.db_client = db_client
        """
        Create three users:
        - USER_ADMIN: a user with DB_WRITE permissions
        - USER_OWNER: a user who owns/creates a data request
        - USER_NON_OWNER: a user who does not own/create a data request
        """
        # Represents an admin
        self.tus_admin = create_test_user_setup(
            self.flask_client, permissions=[PermissionsEnum.DB_WRITE]
        )
        # Represents a user who owns/create a data request
        self.tus_owner = create_test_user_setup(self.flask_client)
        # Represents a user who does not own/create a data request
        self.tus_non_owner = create_test_user_setup(self.flask_client)

        # USER_ADMIN creates a data source
        self.created_data_source = create_data_source_with_endpoint(
            flask_client=self.flask_client,
            jwt_authorization_header=self.tus_admin.jwt_authorization_header,
        )

        # USER_OWNER creates a data request
        self.created_data_request = create_data_request_with_endpoint(
            flask_client=self.flask_client,
            jwt_authorization_header=self.tus_owner.jwt_authorization_header,
        )

    def get_data_request_related_sources_with_given_data_request_id(
        self,
        api_authorization_header: dict,
        expected_json_content: Optional[dict] = None
    ):
        get_data_request_related_sources_with_endpoint(
            flask_client=self.flask_client,
            api_authorization_header=api_authorization_header,
            data_request_id=self.created_data_request.id,
            expected_json_content=expected_json_content,
        )




@pytest.fixture
def related_agencies_test_setup(integration_test_setup: IntegrationTestSetup):
    return DataRequestByRelatedSourcesTestSetup(
        flask_client=integration_test_setup.flask_client,
        db_client=integration_test_setup.db_client,
    )

def test_data_request_by_id_related_sources(
    integration_test_setup: IntegrationTestSetup,
):
    """

    :param ts:
    :return:
    """
    ts = integration_test_setup

    tus_admin = create_test_user_setup(
        ts.flask_client, permissions=[PermissionsEnum.DB_WRITE]
    )
    tus_owner = ts.tus
    tus_non_owner = create_test_user_setup(ts.flask_client)

    # USER_ADMIN creates a data source
    cds = create_data_source_with_endpoint(
        flask_client=ts.flask_client,
        jwt_authorization_header=tus_admin.jwt_authorization_header,
    )

    # USER_OWNER creates a data request
    cdr = create_data_request_with_endpoint(
        flask_client=ts.flask_client,
        jwt_authorization_header=tus_owner.jwt_authorization_header,
    )

    def get_data_request_related_sources_with_given_data_request_id(
        api_authorization_header: dict, expected_json_content: Optional[dict] = None
    ):
        get_data_request_related_sources_with_endpoint(
            flask_client=ts.flask_client,
            api_authorization_header=api_authorization_header,
            data_request_id=cdr.id,
            expected_json_content=expected_json_content,
        )

    # USER_OWNER and USER_NON_OWNER gets related sources of data request, and should see none
    NO_RESULTS_RESPONSE = {"count": 0, "data": [], "message": "Related sources found."}

    get_data_request_related_sources_with_given_data_request_id(
        api_authorization_header=tus_owner.api_authorization_header,
        expected_json_content=NO_RESULTS_RESPONSE,
    )

    get_data_request_related_sources_with_given_data_request_id(
        api_authorization_header=tus_non_owner.api_authorization_header,
        expected_json_content=NO_RESULTS_RESPONSE,
    )

    FORMATTED_DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT = (
        DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT.format(
            data_request_id=cdr.id, source_id=cds.id
        )
    )

    def add_related_source(
        jwt_authorization_header: dict,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        ts.run_and_validate_request(
            http_method="post",
            endpoint=FORMATTED_DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT,
            headers=jwt_authorization_header,
            expected_json_content=expected_json_content,
            expected_response_status=expected_response_status,
        )

    # USER_NON_OWNER tries to add a related source to the data request, and should be denied
    add_related_source(
        jwt_authorization_header=tus_non_owner.jwt_authorization_header,
        expected_json_content={
            "message": "User does not have permission to perform this action."
        },
        expected_response_status=HTTPStatus.FORBIDDEN,
    )
    # USER_OWNER adds a related source to the data request, and should succeed
    add_related_source(
        jwt_authorization_header=tus_owner.jwt_authorization_header,
        expected_json_content={
            "message": "Data source successfully associated with request."
        },
    )
    # USER_ADMIN tries to add the same related source to the data request, and should be denied
    add_related_source(
        jwt_authorization_header=tus_admin.jwt_authorization_header,
        expected_json_content={
            "message": "Request-Source association already exists."
        },
        expected_response_status=HTTPStatus.CONFLICT
    )

    # USER_OWNER and USER_NON_OWNER gets related sources of data request, and should see the one added
    RESULTS_RESPONSE = {
        "count": 1,
        "data": [
            {
                "airtable_uid": cds.id,
                "name": cds.name
            }
        ],
        "message": "Related sources found."
    }

    get_data_request_related_sources_with_given_data_request_id(
        api_authorization_header=tus_owner.api_authorization_header,
        expected_json_content=RESULTS_RESPONSE,
    )

    get_data_request_related_sources_with_given_data_request_id(
        api_authorization_header=tus_non_owner.api_authorization_header,
        expected_json_content=RESULTS_RESPONSE,
    )

    def delete_related_source(
        expected_response_status: HTTPStatus,
        expected_json_response: Optional[dict] = None,
    ):
        run_and_validate_request(
            flask_client=ts.flask_client,
            http_method="delete",
            endpoint=FORMATTED_DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT,
            headers=tus_owner.jwt_authorization_header,
            expected_json_content=expected_json_response,
            expected_response_status=expected_response_status,
        )

    # USER_OWNER deletes the related source of the data request, and succeeds
    delete_related_source(
        expected_json_response={
            "message": "Request-Source association deleted."
        },
        expected_response_status=HTTPStatus.OK,
    )

    # USER_OWNER tries to delete the same related source of the data request, and should be denied
    delete_related_source(expected_response_status=HTTPStatus.NOT_FOUND)

    # USER_OWNER and USER_NON_OWNER gets related sources of data request, and should see none
    get_data_request_related_sources_with_given_data_request_id(
        api_authorization_header=tus_owner.api_authorization_header,
        expected_json_content=NO_RESULTS_RESPONSE,
    )

    get_data_request_related_sources_with_given_data_request_id(
        api_authorization_header=tus_non_owner.api_authorization_header,
        expected_json_content=NO_RESULTS_RESPONSE,
    )
