import uuid

from dataclasses import dataclass
from http import HTTPStatus
from typing import Dict, Optional

import pytest
from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import RequestUrgency
from middleware.constants import DATA_KEY
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_schemas import (
    GetByIDDataRequestsResponseSchema,
    GetManyDataRequestsResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_schemas import (
    DataSourceExpandedSchema,
    DataSourcesGetManySchema,
)
from resources.endpoint_schema_config import SchemaConfigs
from tests.conftest import dev_db_client, flask_client_with_db
from tests.helper_scripts.common_endpoint_calls import create_data_source_with_endpoint
from tests.helper_scripts.common_test_data import (
    create_test_data_request,
    TestDataCreatorFlask,
)
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
    create_test_user_setup, add_query_params,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.helper_classes.IntegrationTestSetup import (
    IntegrationTestSetup,
)
from conftest import test_data_creator_flask, monkeysession


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


def test_data_requests_get(
    test_data_creator_flask: TestDataCreatorFlask,
):

    tdc = test_data_creator_flask
    tdc.clear_test_data()
    # Delete all data from the data requests table
    tdc.db_client.execute_raw_sql("""DELETE FROM data_requests""")

    tus_creator = tdc.standard_user()

    # Creator creates a data request
    dr_info = tdc.data_request(tus_creator)
    # Create a data source and associate with that request
    ds_info = tdc.data_source()
    tdc.link_data_request_to_data_source(
        data_request_id=dr_info.id,
        data_source_id=ds_info.id,
    )

    # Add another data source, and set its approval status to `Active`
    dr_info_2 = tdc.data_request(tus_creator)

    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="put",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
            data_request_id=dr_info_2.id
        ),
        headers=tdc.get_admin_tus().jwt_authorization_header,
        json={"entry_data": {"request_status": "Active"}},
    )


    expected_schema = SchemaConfigs.DATA_REQUESTS_GET_MANY.value.primary_output_schema
    # Modify exclude to account for old data which did not have archive_reason and creator_user_id
    expected_schema.exclude.update(
        ["data.archive_reason", "data.creator_user_id", "data.internal_notes"]
    )
    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=tus_creator.jwt_authorization_header,
        expected_schema=expected_schema,
    )
    assert len(json_data[DATA_KEY]) == 2

    # Validate that at least one entry returned has data_sources
    # TODO: This passes in test but not stage, which uses actual data requests which are not yet linked to data sources.
    # an_entry_has_data_sources = False
    # for entry in json_data[DATA_KEY]:
    #     data_sources = entry["data_sources"]
    #     if len(data_sources) > 0:
    #         DataSourceExpandedSchema().load(data_sources[0])
    #         an_entry_has_data_sources = True
    #         break
    # assert an_entry_has_data_sources

    # Give user admin permission
    tdc.db_client.add_user_permission(
        user_email=tus_creator.user_info.email, permission=PermissionsEnum.DB_WRITE
    )

    admin_json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=tus_creator.jwt_authorization_header,
    )

    # Assert admin columns are greater than user columns
    assert len(admin_json_data[DATA_KEY][0]) > len(json_data[DATA_KEY][0])

    # Run get again, this time filtering the request status to be active
    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=add_query_params(
            url=DATA_REQUESTS_BASE_ENDPOINT,
            params={"request_status": "Active"},
        ),
        headers=tus_creator.jwt_authorization_header,
        expected_schema=expected_schema,
    )

    # The more recent data request should be returned, but the old one should be filtered out
    assert len(json_data[DATA_KEY]) == 1
    assert int(json_data[DATA_KEY][0]["id"]) == int(dr_info_2.id)



def test_data_requests_post(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    standard_tus = tdc.standard_user()

    def post_data_request(
        json_request: dict,
        use_authorization_header=True,
        expected_response_status: HTTPStatus = HTTPStatus.OK
    ) -> dict:
        if use_authorization_header:
            header = standard_tus.jwt_authorization_header
        else:
            header = standard_tus.api_authorization_header
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="post",
            endpoint=DATA_REQUESTS_BASE_ENDPOINT,
            headers=header,
            json=json_request,
            expected_response_status=expected_response_status
        )

    def get_data_request(
        data_request_id: int
    ):
        return run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
            data_request_id=data_request_id
        ),
        headers=standard_tus.jwt_authorization_header,
        expected_schema=SchemaConfigs.DATA_REQUESTS_BY_ID_GET.value.primary_output_schema,
    )


    submission_notes = uuid.uuid4().hex

    location_info_1 = {
        "type": "Locality",
        "state": "California",
        "county": "Orange",
        "locality": 'Laguna Hills',
    }
    location_info_2 = {
        "type": "Locality",
        "state": "California",
        "county": "Orange",
        "locality": 'Seal Beach',
    }

    json_request = {
            "request_info": {
                "submission_notes": submission_notes,
                "title": uuid.uuid4().hex,
                "request_urgency": RequestUrgency.URGENT.value,
                "coverage_range": "2000-2005"
            },
            "location_infos": [
                location_info_1,
                location_info_2
            ]

        }

    json_data = post_data_request(json_request)

    # Test that data request was created and can now be retrieved
    json_data = get_data_request(json_data["id"])

    data = json_data[DATA_KEY]

    assert len(data) > 0
    locations = data["locations"]
    assert len(locations) == 2
    for location in locations:
        if location["locality_name"] == location_info_1["locality"]:
            continue
        if location["locality_name"] == location_info_2["locality"]:
            continue
        assert False


    assert data["submission_notes"] == submission_notes
    user_id = tdc.db_client.get_user_id(standard_tus.user_info.email)
    assert data["creator_user_id"] == user_id
    assert data["request_urgency"] == RequestUrgency.URGENT.value

    # Test that if no location info is provided, the result has no locations associated with it
    json_request = {
        "request_info": {
            "submission_notes": submission_notes,
            "title": uuid.uuid4().hex,
            "request_urgency": RequestUrgency.URGENT.value,
        },
    }
    json_data = post_data_request(json_request)
    json_data = get_data_request(json_data["id"])
    data = json_data[DATA_KEY]

    locations = data["locations"]
    assert len(locations) == 0


    # Check that response is forbidden for standard user using API header
    post_data_request(
        json_request,
        use_authorization_header=False,
        expected_response_status=HTTPStatus.UNAUTHORIZED
    )

    # Check that response fails if using invalid columns
    post_data_request(
        json_request={
            "request_info": {
                "submission_notes": submission_notes,
                "title": uuid.uuid4().hex,
                "request_urgency": RequestUrgency.URGENT.value,
                "invalid_column": uuid.uuid4().hex
            }
        },
        expected_response_status=HTTPStatus.BAD_REQUEST,
    )


def test_data_requests_by_id_get(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    admin_tus = tdc.get_admin_tus()

    tdr = tdc.data_request(admin_tus)

    expected_schema = SchemaConfigs.DATA_REQUESTS_BY_ID_GET.value.primary_output_schema
    # Modify exclude to account for old data which did not have archive_reason and creator_user_id
    expected_schema.exclude.update(
        ["data.archive_reason", "data.creator_user_id", "data.internal_notes"]
    )

    # Run with API header
    api_json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
            data_request_id=tdr.id
        ),
        headers=admin_tus.api_authorization_header,
        expected_schema=expected_schema,
    )

    assert api_json_data[DATA_KEY]["submission_notes"] == tdr.submission_notes

    # Run with JWT header
    jwt_json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
            data_request_id=tdr.id
        ),
        headers=admin_tus.jwt_authorization_header,
        expected_schema=expected_schema,
    )

    assert jwt_json_data[DATA_KEY]["submission_notes"] == tdr.submission_notes

    #  Confirm elevated user has more columns than standard user
    assert len(jwt_json_data[DATA_KEY].keys()) > len(api_json_data[DATA_KEY].keys())


def test_data_requests_by_id_put(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    standard_tus = tdc.standard_user()

    tdr = tdc.data_request(standard_tus)
    data_request_id = tdr.id

    new_submission_notes = str(uuid.uuid4())

    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="put",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
            data_request_id=data_request_id
        ),
        headers=standard_tus.jwt_authorization_header,
        json={"entry_data": {"submission_notes": new_submission_notes}},
    )

    result = tdc.db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings=[WhereMapping(column="id", value=int(data_request_id))],
    )

    assert result[0]["submission_notes"] == new_submission_notes

    # Check that request is denied on admin-only column
    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="put",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
            data_request_id=data_request_id
        ),
        headers=standard_tus.jwt_authorization_header,
        json={"entry_data": {"request_status": "approved"}},
        expected_response_status=HTTPStatus.FORBIDDEN,
    )


def test_data_requests_by_id_delete(test_data_creator_flask):
    tdc = test_data_creator_flask

    tus_admin = tdc.get_admin_tus()
    tus_owner = tdc.standard_user()
    tus_non_owner = tdc.standard_user()

    flask_client = tdc.flask_client

    tdr = tdc.data_request(tus_owner)

    data_request_id = int(tdr.id)

    # Owner should be able to delete their own request
    json_data = run_and_validate_request(
        flask_client=flask_client,
        http_method="delete",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
            data_request_id=data_request_id
        ),
        headers=tus_owner.jwt_authorization_header,
    )

    assert (
        tdc.db_client.get_data_requests(
            columns=["submission_notes"],
            where_mappings=[WhereMapping(column="id", value=data_request_id)],
        )
        == []
    )

    # Check that request is denied if user is not owner and does not have DB_WRITE permission
    new_tdr = create_test_data_request(flask_client, tus_owner.jwt_authorization_header)

    NEW_ENDPOINT = DATA_REQUESTS_BY_ID_ENDPOINT.format(data_request_id=new_tdr.id)

    run_and_validate_request(
        flask_client=flask_client,
        http_method="delete",
        endpoint=NEW_ENDPOINT,
        headers=tus_non_owner.jwt_authorization_header,
        expected_response_status=HTTPStatus.FORBIDDEN,
    )

    # But if user is an admin, allow
    run_and_validate_request(
        flask_client=flask_client,
        http_method="delete",
        endpoint=NEW_ENDPOINT,
        headers=tus_admin.jwt_authorization_header,
    )

    # If data request id doesn't exist (or is already deleted), return 404
    run_and_validate_request(
        flask_client=flask_client,
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
        expected_schema=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_GET.value.primary_output_schema,
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
        self.created_data_request = create_test_data_request(
            flask_client=self.flask_client,
            jwt_authorization_header=self.tus_owner.jwt_authorization_header,
        )

    def get_data_request_related_sources_with_given_data_request_id(
        self,
        api_authorization_header: dict,
        expected_json_content: Optional[dict] = None,
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
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    flask_client = tdc.flask_client

    tus_admin = tdc.get_admin_tus()
    tus_owner = tdc.standard_user()
    tus_non_owner = tdc.standard_user()

    # USER_ADMIN creates a data source
    cds = tdc.data_source()

    # USER_OWNER creates a data request
    cdr = tdc.data_request(tus_owner)

    def get_data_request_related_sources_with_given_data_request_id(
        api_authorization_header: dict, expected_json_content: Optional[dict] = None
    ):
        return get_data_request_related_sources_with_endpoint(
            flask_client=flask_client,
            api_authorization_header=api_authorization_header,
            data_request_id=cdr.id,
            expected_json_content=expected_json_content,
        )

    # USER_OWNER and USER_NON_OWNER gets related sources of data request, and should see none
    NO_RESULTS_RESPONSE = {"metadata": {"count": 0}, "data": [], "message": "Related sources found."}

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
        run_and_validate_request(
            flask_client=flask_client,
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
        expected_json_content={"message": "Request-Source association already exists."},
        expected_response_status=HTTPStatus.CONFLICT,
    )

    # USER_OWNER and USER_NON_OWNER gets related sources of data request, and should see the one added

    response_json_owner = get_data_request_related_sources_with_given_data_request_id(
        api_authorization_header=tus_owner.api_authorization_header,
    )

    response_json_nonowner = (
        get_data_request_related_sources_with_given_data_request_id(
            api_authorization_header=tus_non_owner.api_authorization_header,
        )
    )
    assert response_json_owner == response_json_nonowner
    assert response_json_owner["metadata"]["count"] == 1

    def delete_related_source(
        expected_response_status: HTTPStatus,
        expected_json_response: Optional[dict] = None,
    ):
        run_and_validate_request(
            flask_client=flask_client,
            http_method="delete",
            endpoint=FORMATTED_DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT,
            headers=tus_owner.jwt_authorization_header,
            expected_json_content=expected_json_response,
            expected_response_status=expected_response_status,
        )

    # USER_OWNER deletes the related source of the data request, and succeeds
    delete_related_source(
        expected_json_response={"message": "Request-Source association deleted."},
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
