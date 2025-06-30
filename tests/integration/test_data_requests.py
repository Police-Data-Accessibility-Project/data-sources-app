import uuid

from http import HTTPStatus
from typing import Dict, Optional

from flask.testing import FlaskClient

from db.db_client_dataclasses import WhereMapping
from db.enums import RequestUrgency, LocationType, RequestStatus, SortOrder
from endpoints.schema_config.instantiations.data_requests.by_id.get import (
    DataRequestsByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.related_locations.get import (
    DataRequestsRelatedLocationsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.related_sources.get import (
    DataRequestsRelatedSourcesGetEndpointSchemaConfig,
)
from middleware.constants import DATA_KEY
from middleware.enums import RecordTypes
from middleware.util.type_conversion import get_enum_values
from endpoints.schema_config.enums import SchemaConfigs
from tests.helper_scripts.common_test_data import (
    get_random_number_for_testing,
    get_test_name,
)
from tests.helper_scripts.complex_test_data_creation_functions import (
    create_test_data_request,
)
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.constants import (
    DATA_REQUESTS_BASE_ENDPOINT,
    DATA_REQUESTS_BY_ID_ENDPOINT,
    DATA_REQUESTS_GET_RELATED_SOURCE_ENDPOINT,
    DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT,
    DATA_REQUESTS_RELATED_LOCATIONS,
)

from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup

from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_data_requests_get(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    # Delete all data from the data requests table
    tdc.db_client.execute_raw_sql("""DELETE FROM data_requests""")
    tdc.clear_test_data()

    tus_creator = tdc.standard_user()

    # Creator creates a data request
    dr_info = tdc.data_request(tus_creator)
    # Create a data source and associate with that request
    ds_info = tdc.data_source()
    tdc.link_data_request_to_data_source(
        data_request_id=dr_info.id,
        data_source_id=ds_info.id,
    )

    # Add another data_request, and set its approval status to `Active`
    dr_info_2 = tdc.data_request(tus_creator)

    tdc.request_validator.update_data_request(
        data_request_id=dr_info_2.id,
        headers=tdc.get_admin_tus().jwt_authorization_header,
        entry_data={"request_status": "Active"},
    )

    data = tdc.request_validator.get_data_requests(
        headers=tus_creator.jwt_authorization_header,
    )[DATA_KEY]

    assert len(data) == 2

    # Add another data request, set its approval status to `Archived`
    # THen perform a search for both Active and Archived
    dr_info_3 = tdc.data_request(tus_creator)

    tdc.request_validator.update_data_request(
        data_request_id=dr_info_3.id,
        headers=tdc.get_admin_tus().jwt_authorization_header,
        entry_data={"request_status": "Archived"},
    )

    data = tdc.request_validator.get_data_requests(
        headers=tus_creator.jwt_authorization_header,
        request_statuses=[RequestStatus.ACTIVE, RequestStatus.ARCHIVED],
    )[DATA_KEY]

    assert len(data) == 2

    # Check that admin can pull more columns

    admin_data = tdc.request_validator.get_data_requests(
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )[DATA_KEY]

    # Assert admin columns are greater than user columns
    assert len(admin_data[0]) > len(data[0])

    # Run get again, this time filtering the request status to be active
    data = tdc.request_validator.get_data_requests(
        headers=tus_creator.jwt_authorization_header,
        request_statuses=[RequestStatus.ACTIVE],
    )[DATA_KEY]

    # The more recent data request should be returned, but the old one should be filtered out
    assert len(data) == 1
    assert int(data[0]["id"]) == int(dr_info_2.id)

    # Create additional intake data request to populate
    tdc.data_request(tus_creator)

    # Test sorting
    def get_sorted_data_requests(sort_order: SortOrder):
        return tdc.request_validator.get_data_requests(
            headers=tus_creator.jwt_authorization_header,
            request_statuses=[RequestStatus.INTAKE],
            sort_by="id",
            sort_order=sort_order,
        )

    data_asc = get_sorted_data_requests(SortOrder.ASCENDING)[DATA_KEY]
    data_desc = get_sorted_data_requests(SortOrder.DESCENDING)[DATA_KEY]

    assert int(data_asc[0]["id"]) < int(data_desc[0]["id"])

    # Test limit
    data = tdc.request_validator.get_data_requests(
        headers=tus_creator.jwt_authorization_header,
        limit=1,
    )[DATA_KEY]

    assert len(data) == 1


def test_data_requests_post(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    standard_tus = tdc.standard_user()

    def post_data_request(
        json_request: dict,
        use_authorization_header=True,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
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
            expected_response_status=expected_response_status,
        )

    def get_data_request(data_request_id: int):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="get",
            endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
                data_request_id=data_request_id
            ),
            headers=standard_tus.jwt_authorization_header,
            expected_schema=DataRequestsByIDGetEndpointSchemaConfig.primary_output_schema,
        )

    submission_notes = uuid.uuid4().hex

    location_id_1 = tdc.locality(locality_name="Laguna Hills")
    location_id_2 = tdc.locality(locality_name="Seal Beach")

    json_request = {
        "request_info": {
            "submission_notes": submission_notes,
            "title": get_test_name(),
            "data_requirements": uuid.uuid4().hex,
            "request_urgency": RequestUrgency.URGENT.value,
            "coverage_range": "2000-2005",
        },
        "location_ids": [location_id_1, location_id_2],
    }

    json_data = post_data_request(json_request)

    # Test that data request was created and can now be retrieved
    json_data = get_data_request(json_data["id"])

    data = json_data[DATA_KEY]

    assert len(data) > 0
    locations = data["locations"]
    assert len(locations) == 2
    for location in locations:
        if location["locality_name"] == "Laguna Hills":
            continue
        if location["locality_name"] == "Seal Beach":
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
            "title": get_test_name(),
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
        expected_response_status=HTTPStatus.BAD_REQUEST,
    )

    # Check that response fails if using invalid columns
    post_data_request(
        json_request={
            "request_info": {
                "submission_notes": submission_notes,
                "title": get_test_name(),
                "request_urgency": RequestUrgency.URGENT.value,
                "invalid_column": uuid.uuid4().hex,
            }
        },
        expected_response_status=HTTPStatus.BAD_REQUEST,
    )

    # Check that response fails if title is too long
    post_data_request(
        json_request={
            "request_info": {
                "submission_notes": submission_notes,
                "title": get_test_name() * 100,
                "request_urgency": RequestUrgency.URGENT.value,
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

    # Create data source and link to data request
    data_source_id = tdc.data_source().id
    tdc.link_data_request_to_data_source(
        data_source_id=data_source_id, data_request_id=tdr.id
    )

    expected_schema = DataRequestsByIDGetEndpointSchemaConfig.primary_output_schema
    # Modify exclude to account for old data which did not have archive_reason and creator_user_id
    expected_schema.exclude.update(
        ["data.archive_reason", "data.creator_user_id", "data.internal_notes"]
    )

    # Run with API header
    api_json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(data_request_id=tdr.id),
        headers=admin_tus.api_authorization_header,
        expected_schema=expected_schema,
    )

    assert api_json_data[DATA_KEY]["submission_notes"] == tdr.submission_notes
    assert api_json_data[DATA_KEY]["data_sources"][0]["id"] == int(data_source_id)

    # Run with JWT header
    jwt_json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(data_request_id=tdr.id),
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

    endpoint = DATA_REQUESTS_BY_ID_ENDPOINT.format(data_request_id=data_request_id)

    def put(
        header: dict, json: dict, expected_response_status: HTTPStatus = HTTPStatus.OK
    ):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="put",
            endpoint=endpoint,
            headers=header,
            json=json,
            expected_response_status=expected_response_status,
        )

    put(
        header=standard_tus.jwt_authorization_header,
        json={
            "entry_data": {
                "submission_notes": new_submission_notes,
                "title": get_test_name(),
                "request_urgency": RequestUrgency.URGENT.value,
                "data_requirements": uuid.uuid4().hex,
                "coverage_range": uuid.uuid4().hex,
            }
        },
    )

    result = tdc.db_client.get_data_requests(
        columns=["submission_notes"],
        where_mappings=[WhereMapping(column="id", value=int(data_request_id))],
    )

    assert result[0]["submission_notes"] == new_submission_notes

    # Check that request is denied on admin-only column
    put(
        header=standard_tus.jwt_authorization_header,
        json={"entry_data": {"request_status": "Ready to start"}},
        expected_response_status=HTTPStatus.FORBIDDEN,
    )

    # Successfully edit all possible columns an admin can edit
    put(
        header=tdc.get_admin_tus().jwt_authorization_header,
        json={
            "entry_data": {
                "submission_notes": new_submission_notes,
                "title": get_test_name(),
                "request_urgency": RequestUrgency.URGENT.value,
                "data_requirements": uuid.uuid4().hex,
                "coverage_range": uuid.uuid4().hex,
                "request_status": RequestStatus.READY_TO_START.value,
                "internal_notes": uuid.uuid4().hex,
                "archive_reason": uuid.uuid4().hex,
                "github_issue_url": uuid.uuid4().hex,
                "github_issue_number": get_random_number_for_testing(),
                "pdap_response": uuid.uuid4().hex,
                "record_types_required": get_enum_values(RecordTypes),
            }
        },
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
    run_and_validate_request(
        flask_client=flask_client,
        http_method="delete",
        endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(data_request_id=data_request_id),
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
        expected_schema=DataRequestsRelatedSourcesGetEndpointSchemaConfig.primary_output_schema,
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
    NO_RESULTS_RESPONSE = {
        "metadata": {"count": 0},
        "data": [],
        "message": "Related sources found.",
    }

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


def test_link_unlink_data_requests_with_locations(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    cdr = tdc.data_request()
    admin_tus = tdc.get_admin_tus()

    location_get_endpoint = DATA_REQUESTS_RELATED_LOCATIONS.format(
        data_request_id=cdr.id
    )

    def get_locations(
        tus: TestUserSetup = admin_tus,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=DataRequestsRelatedLocationsGetEndpointSchemaConfig.primary_output_schema,
    ):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="get",
            endpoint=location_get_endpoint,
            headers=tus.jwt_authorization_header,
            expected_response_status=expected_response_status,
            expected_schema=expected_schema,
        )["data"]

    data = get_locations()
    assert data == []

    # Add location
    location_id = tdc.locality("Pittsburgh")

    def post_location_association(
        tus: TestUserSetup = admin_tus,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_DELETE.value.primary_output_schema,
        expected_json_content: Optional[dict] = None,
    ):
        return tdc.request_validator.link_data_request_with_location(
            data_request_id=cdr.id,
            location_id=location_id,
            headers=tus.jwt_authorization_header,
            expected_response_status=expected_response_status,
            expected_schema=expected_schema,
            expected_json_content=expected_json_content,
        )

    post_location_association(
        expected_json_content={
            "message": "Location successfully associated with request."
        }
    )

    data = get_locations()
    assert data == [
        {
            "location_id": location_id,
            "state_name": "Pennsylvania",
            "state_iso": "PA",
            "county_name": "Allegheny",
            "county_fips": "42003",
            "locality_name": "Pittsburgh",
            "type": LocationType.LOCALITY.value,
        }
    ]

    def delete_location_association(
        tus: TestUserSetup = admin_tus,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_DELETE.value.primary_output_schema,
        expected_json_content: Optional[dict] = None,
    ):
        tdc.request_validator.unlink_data_request_with_location(
            data_request_id=cdr.id,
            location_id=location_id,
            headers=tus.jwt_authorization_header,
            expected_response_status=expected_response_status,
            expected_schema=expected_schema,
            expected_json_content=expected_json_content,
        )

    # Test that a standard user add or remove a location association
    standard_tus = tdc.standard_user()

    post_location_association(
        tus=standard_tus,
        expected_response_status=HTTPStatus.FORBIDDEN,
        expected_schema=None,
    )

    delete_location_association(
        tus=standard_tus,
        expected_response_status=HTTPStatus.FORBIDDEN,
        expected_schema=None,
    )

    # Finally delete the location association
    delete_location_association(
        expected_json_content={"message": "Request-Location association deleted."}
    )

    data = get_locations()
    assert data == []


def test_data_request_withdraw(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    tus_owner = tdc.standard_user()
    data_request = tdc.data_request(user_tus=tus_owner)

    tdc.request_validator.withdraw_request(
        data_request_id=data_request.id, headers=tus_owner.jwt_authorization_header
    )

    request_status = tdc.request_validator.get_data_request_by_id(
        data_request_id=data_request.id, headers=tus_owner.jwt_authorization_header
    )["data"]["request_status"]

    assert request_status == RequestStatus.REQUEST_WITHDRAWN.value

    # Test that this works for an admin user as well
    tus_admin = tdc.get_admin_tus()
    data_request = tdc.data_request(user_tus=tus_owner)

    tdc.request_validator.withdraw_request(
        data_request_id=data_request.id, headers=tus_admin.jwt_authorization_header
    )

    request_status = tdc.request_validator.get_data_request_by_id(
        data_request_id=data_request.id, headers=tus_admin.jwt_authorization_header
    )["data"]["request_status"]

    assert request_status == RequestStatus.REQUEST_WITHDRAWN.value

    # Test that this doesn't work for a standard user who is not the owner
    tus_non_owner = tdc.standard_user()
    data_request = tdc.data_request(user_tus=tus_owner)

    tdc.request_validator.withdraw_request(
        data_request_id=data_request.id,
        headers=tus_non_owner.jwt_authorization_header,
        expected_response_status=HTTPStatus.FORBIDDEN,
    )
