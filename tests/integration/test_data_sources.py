"""Integration tests for /data-sources endpoint"""

import urllib.parse
import uuid

import psycopg

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import (
    LocationType,
    AgencyAggregation,
    DetailLevel,
    AccessType,
    RetentionSchedule,
    URLStatus,
    ApprovalStatus,
    UpdateMethod,
)
from middleware.enums import AccessTypeEnum, RecordType

from resources.endpoint_schema_config import SchemaConfigs
from tests.conftest import (
    flask_client_with_db,
    test_user_admin,
)
from conftest import test_data_creator_flask, monkeysession
from tests.helper_scripts.common_endpoint_calls import create_data_source_with_endpoint
from tests.helper_scripts.common_test_data import TestDataCreatorFlask
from tests.helper_scripts.helper_functions import (
    get_boolean_dictionary,
    create_test_user_setup,
    search_with_boolean_dictionary,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.constants import (
    DATA_SOURCES_BASE_ENDPOINT,
    DATA_SOURCES_GET_RELATED_AGENCIES_ENDPOINT,
    DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT,
)


def test_data_sources_get(flask_client_with_db):
    """
    Test that GET call to /data-sources endpoint retrieves data sources and correctly identifies specific sources by name
    """
    tus = create_test_user_setup(flask_client_with_db)
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}?page=1&approval_status=approved",  # ENDPOINT,
        headers=tus.api_authorization_header,
        expected_schema=SchemaConfigs.DATA_SOURCES_GET_MANY.value.primary_output_schema,
    )
    data = response_json["data"]
    assert len(data) == 100

    # Test sort functionality
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}?page=1&sort_by=name&sort_order=ASC&approval_status=approved",
        headers=tus.api_authorization_header,
        expected_schema=SchemaConfigs.DATA_SOURCES_GET_MANY.value.primary_output_schema,
    )
    data_asc = response_json["data"]

    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}?page=1&sort_by=name&sort_order=DESC&approval_status=approved",
        headers=tus.api_authorization_header,
    )
    data_desc = response_json["data"]

    assert data_asc[0]["name"] < data_desc[0]["name"]


def test_data_sources_get_many_limit_columns(flask_client_with_db):
    """
    Test that GET call to /data-sources endpoint properly limits by columns
     when passed the `requested_columns` query parameter
    """

    tus = create_test_user_setup(flask_client_with_db)
    allowed_columns = ["name", "submitted_name", "id"]
    url_encoded_column_string = urllib.parse.quote_plus(str(allowed_columns))
    expected_schema = SchemaConfigs.DATA_SOURCES_GET_MANY.value.primary_output_schema
    expected_schema.only = [
        "message",
        "metadata",
        "data.name",
        "data.submitted_name",
        "data.id",
    ]
    expected_schema.partial = True

    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
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
    cds = tdc.data_source()

    rows = tdc.db_client.execute_raw_sql(
        query="""
        SELECT * from data_sources WHERE name=%s
        """,
        vars=(cds.name,),
    )
    len(rows) == 1


def test_data_sources_by_id_get(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /data-sources-by-id/<data_source_id> endpoint retrieves the data source with the correct homepage URL
    """

    tus = create_test_user_setup(test_data_creator_flask.flask_client)
    cds = test_data_creator_flask.data_source()
    response_json = run_and_validate_request(
        flask_client=test_data_creator_flask.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{cds.id}",
        headers=tus.api_authorization_header,
        expected_schema=SchemaConfigs.DATA_SOURCES_GET_BY_ID.value.primary_output_schema,
    )

    assert response_json["data"]["name"] == cds.name


def test_data_sources_by_id_put(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that PUT call to /data-sources-by-id/<data_source_id> endpoint successfully updates the description of the data source and verifies the change in the database
    """
    tdc = test_data_creator_flask
    cdr = tdc.data_source()

    entry_data = {
        "submitted_name": uuid.uuid4().hex,
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
        "scraper_url": uuid.uuid4().hex,
        "submission_notes": uuid.uuid4().hex,
        "submitter_contact_info": uuid.uuid4().hex,
        "agency_described_submitted": uuid.uuid4().hex,
        "agency_described_not_in_database": uuid.uuid4().hex,
        "data_portal_type_other": uuid.uuid4().hex,
        "access_notes": uuid.uuid4().hex,
        "url_status": URLStatus.OK.value,
        "approval_status": ApprovalStatus.APPROVED.value,
        "record_type_name": RecordType.ARREST_RECORDS.value,
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
    for key, value in entry_data.items():
        assert data[key] == value


def test_data_sources_by_id_delete(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that DELETE call to /data-sources-by-id/<data_source_id> endpoint successfully deletes the data source and verifies the change in the database
    """
    # Insert new entry
    tdc = test_data_creator_flask

    ds_info = tdc.data_source()

    result = tdc.db_client.get_data_sources(
        columns=["description"],
        where_mappings=[WhereMapping(column="id", value=int(ds_info.id))],
    )
    assert len(result) == 1

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="delete",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{ds_info.id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    result = tdc.db_client.get_data_sources(
        columns=["description"],
        where_mappings=[WhereMapping(column="id", value=int(ds_info.id))],
    )

    assert len(result) == 0


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
            expected_schema=SchemaConfigs.AGENCIES_GET_MANY.value.primary_output_schema,
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
