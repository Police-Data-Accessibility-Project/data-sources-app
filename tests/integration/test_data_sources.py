"""Integration tests for /data-sources endpoint"""

import urllib.parse
import uuid
from http import HTTPStatus

from db.enums import (
    AgencyAggregation,
    DetailLevel,
    AccessType,
    RetentionSchedule,
    URLStatus,
    ApprovalStatus,
    UpdateMethod,
    SortOrder,
)
from middleware.enums import RecordTypes
from middleware.schema_and_dto.schemas.data_sources.expanded import (
    DataSourceExpandedSchema,
)

from endpoints.schema_config import SchemaConfigs

from tests.conftest import test_data_creator_flask
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import (
    TestDataCreatorDBClient,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.common_asserts import assert_contains_key_value_pairs
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.constants import (
    DATA_SOURCES_BASE_ENDPOINT,
    DATA_SOURCES_GET_RELATED_AGENCIES_ENDPOINT,
    DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT,
)
from tests.integration.test_check_database_health import wipe_database


def test_data_sources_get(
    test_data_creator_flask: TestDataCreatorFlask,
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    """
    Test that GET call to /data-sources endpoint retrieves data sources and correctly identifies specific sources by name
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()
    for i in range(100):
        test_data_creator_db_client.data_source(approval_status=ApprovalStatus.APPROVED)
    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
    )
    data = response_json["data"]
    assert len(data) == 100

    # Test sort functionality
    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.ASCENDING,
    )
    data_asc = response_json["data"]

    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.DESCENDING,
    )
    data_desc = response_json["data"]

    assert data_asc[0]["name"] < data_desc[0]["name"]

    # Test limit functionality
    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        limit=10,
    )
    data = response_json["data"]
    assert len(data) == 10


def test_data_source_get_filter_by_approval_status(
    test_data_creator_flask: TestDataCreatorFlask, test_data_creator_db_client
):
    """
    Test that GET call to /data-sources endpoint retrieves data sources and correctly identifies specific sources by name
    """
    tdc = test_data_creator_flask
    wipe_database(tdc.db_client)
    tus = tdc.standard_user()
    test_data_creator_db_client.data_source(approval_status=ApprovalStatus.PENDING)

    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        approval_status=ApprovalStatus.PENDING,
    )
    data = response_json["data"]
    assert len(data) == 1

    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        approval_status=ApprovalStatus.APPROVED,
    )
    data = response_json["data"]
    assert len(data) == 0


def test_data_sources_get_many_limit_columns(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that GET call to /data-sources endpoint properly limits by columns
     when passed the `requested_columns` query parameter
    """
    tdc = test_data_creator_flask
    tdc.data_source()

    tus = tdc.standard_user()
    allowed_columns = ["name", "id"]
    url_encoded_column_string = urllib.parse.quote_plus(str(allowed_columns))
    expected_schema = SchemaConfigs.DATA_SOURCES_GET_MANY.value.primary_output_schema
    expected_schema.only = [
        "message",
        "metadata",
        "data.name",
        "data.id",
    ]
    expected_schema.partial = True

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}?page=1&requested_columns={url_encoded_column_string}",
        headers=tus.api_authorization_header,
        expected_schema=expected_schema,
    )
    data = response_json["data"]

    entry = data[0]
    for column in allowed_columns:
        assert column in entry


def test_data_sources_post(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that POST call to /data-sources endpoint successfully creates a new data source with a unique name and verifies its existence in the database
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    agency_id = tdc.agency().id

    entry_data = generate_test_data_from_schema(
        schema=DataSourceExpandedSchema(
            exclude=[
                "id",
                "updated_at",
                "created_at",
                "record_type_id",
                "broken_source_url_as_of",
                "approval_status_updated_at",
                "last_approval_editor",
                "last_approval_editor_old",
            ],
        ),
    )

    response_json = tdc.request_validator.post(
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}",
        headers=tus.jwt_authorization_header,
        json={
            "entry_data": entry_data,
            "linked_agency_ids": [agency_id],
        },
        expected_schema=SchemaConfigs.DATA_SOURCES_POST.value.primary_output_schema,
    )

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{response_json['id']}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        expected_schema=SchemaConfigs.DATA_SOURCES_GET_BY_ID.value.primary_output_schema,
    )

    assert_contains_key_value_pairs(
        dict_to_check=response_json["data"],
        key_value_pairs=entry_data,
    )

    agencies = response_json["data"]["agencies"]
    assert len(agencies) == 1
    assert agencies[0]["id"] == int(agency_id)


def test_data_sources_by_id_get(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /data-sources-by-id/<data_source_id> endpoint retrieves the data source with the correct homepage URL
    """
    tdc = test_data_creator_flask

    tus = tdc.standard_user()
    cds = tdc.data_source()

    # Create agency and link to data source
    agency_id = tdc.agency().id
    tdc.link_data_source_to_agency(data_source_id=cds.id, agency_id=agency_id)

    # Create data request and link to data source
    request_id = tdc.data_request(tus).id
    tdc.link_data_request_to_data_source(
        data_source_id=cds.id, data_request_id=request_id
    )

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{cds.id}",
        headers=tus.api_authorization_header,
        expected_schema=SchemaConfigs.DATA_SOURCES_GET_BY_ID.value.primary_output_schema,
    )

    data = response_json["data"]
    assert data["name"] == cds.name
    assert data["data_requests"][0]["id"] == int(request_id)
    assert data["agencies"][0]["id"] == int(agency_id)


def test_data_sources_by_id_put(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that PUT call to /data-sources-by-id/<data_source_id> endpoint successfully updates the description of the data source and verifies the change in the database
    """
    tdc = test_data_creator_flask
    cdr = tdc.data_source()

    entry_data = {
        "name": get_test_name(),
        "description": uuid.uuid4().hex,
        "source_url": uuid.uuid4().hex,
        "agency_supplied": True,
        "supplying_entity": uuid.uuid4().hex,
        "agency_originated": True,
        "agency_aggregation": AgencyAggregation.FEDERAL.value,
        "coverage_start": "2020-01-01",
        "coverage_end": "2020-12-31",
        "detail_level": DetailLevel.INDIVIDUAL.value,
        "access_types": [
            AccessType.API.value,
            AccessType.WEB_PAGE.value,
            AccessType.DOWNLOAD.value,
        ],
        "data_portal_type": uuid.uuid4().hex,
        "record_formats": [uuid.uuid4().hex, uuid.uuid4().hex],
        "update_method": UpdateMethod.INSERT.value,
        "tags": [uuid.uuid4().hex, uuid.uuid4().hex],
        "readme_url": uuid.uuid4().hex,
        "originating_entity": uuid.uuid4().hex,
        "retention_schedule": RetentionSchedule.ONE_TO_TEN_YEARS.value,
        "rejection_note": uuid.uuid4().hex,
        "scraper_url": uuid.uuid4().hex,
        "submission_notes": uuid.uuid4().hex,
        "submitter_contact_info": uuid.uuid4().hex,
        "agency_described_not_in_database": uuid.uuid4().hex,
        "data_portal_type_other": uuid.uuid4().hex,
        "access_notes": uuid.uuid4().hex,
        "url_status": URLStatus.OK.value,
        "record_type_name": RecordTypes.ARREST_RECORDS.value,
    }

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="put",
        endpoint=f"/api/data-sources/{cdr.id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        json={"entry_data": entry_data},
    )

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{cdr.id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        expected_schema=SchemaConfigs.DATA_SOURCES_GET_BY_ID.value.primary_output_schema,
    )

    data = response_json["data"]
    assert_contains_key_value_pairs(
        dict_to_check=data,
        key_value_pairs=entry_data,
    )

    # Test that last_approval_editor is None
    assert data["last_approval_editor"] is None


def test_data_sources_by_id_put_approval_status(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that PUT call to /data-sources-by-id/<data_source_id> endpoint successfully updates the last_approval_editor of the data source and verifies the change in the database
    """
    tdc = test_data_creator_flask
    cdr = tdc.data_source()

    entry_data = {"approval_status": ApprovalStatus.APPROVED.value}

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="put",
        endpoint=f"/api/data-sources/{cdr.id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        json={"entry_data": entry_data},
    )

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{cdr.id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        expected_schema=SchemaConfigs.DATA_SOURCES_GET_BY_ID.value.primary_output_schema,
    )

    data = response_json["data"]
    assert_contains_key_value_pairs(
        dict_to_check=data,
        key_value_pairs=entry_data,
    )

    # Test that last_approval_editor is the user
    assert data["last_approval_editor"] == tdc.get_admin_tus().user_info.user_id


def test_data_sources_by_id_delete(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that DELETE call to /data-sources-by-id/<data_source_id> endpoint successfully deletes the data source and verifies the change in the database
    """
    # Insert new entry
    tdc = test_data_creator_flask

    ds_info = tdc.data_source()

    result = tdc.db_client.get_data_source_by_id(
        data_source_id=int(ds_info.id),
        data_sources_columns=["id"],
        data_requests_columns=[],
    )
    assert result is not None

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="delete",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{ds_info.id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    result = tdc.db_client.get_data_source_by_id(
        data_source_id=int(ds_info.id),
        data_sources_columns=["id"],
        data_requests_columns=[],
    )

    assert result is None


def test_data_source_by_id_related_agencies(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask

    # Create data source
    ds_info = tdc.data_source()

    # Confirm no agencies associated with data source yet

    def get_related_agencies():
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="get",
            endpoint=DATA_SOURCES_GET_RELATED_AGENCIES_ENDPOINT.format(
                data_source_id=ds_info.id
            ),
            headers=tdc.get_admin_tus().jwt_authorization_header,
            expected_schema=SchemaConfigs.DATA_SOURCES_RELATED_AGENCIES_GET.value.primary_output_schema,
        )

    json_data = get_related_agencies()
    assert len(json_data["data"]) == 0
    assert json_data["metadata"]["count"] == 0

    # Create agency
    agency_info = tdc.agency()

    # Associate agency with data source
    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT.format(
            data_source_id=ds_info.id, agency_id=agency_info.id
        ),
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    # Confirm agency is associated with data source

    json_data = get_related_agencies()
    assert len(json_data["data"]) == 1
    assert json_data["metadata"]["count"] == 1
    assert json_data["data"][0]["id"] == int(agency_info.id)

    # Delete association

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="delete",
        endpoint=DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT.format(
            data_source_id=ds_info.id, agency_id=agency_info.id
        ),
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    # Confirm agency is no longer associated with data source

    json_data = get_related_agencies()
    assert len(json_data["data"]) == 0
    assert json_data["metadata"]["count"] == 0


def test_data_sources_reject_happy_path(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    data_source = tdc.data_source()

    header = tdc.get_admin_tus().jwt_authorization_header

    def check_data_source_status(approval_status: ApprovalStatus):
        json_data = tdc.request_validator.get_data_source_by_id(
            headers=header, id=data_source.id
        )

        assert json_data["data"]["approval_status"] == approval_status.value

    check_data_source_status(ApprovalStatus.APPROVED)

    tdc.request_validator.reject_data_source(
        headers=header,
        data_source_id=data_source.id,
        rejection_note="This data source is not appropriate for our system",
        expected_json_content={
            "message": "Successfully rejected data source.",
        },
    )

    check_data_source_status(ApprovalStatus.REJECTED)


def test_data_sources_reject_wrong_authorization(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask

    data_source = tdc.data_source()

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=f"/api/data-sources/{data_source.id}/reject",
        headers=tdc.standard_user().jwt_authorization_header,
        expected_response_status=HTTPStatus.FORBIDDEN,
    )
