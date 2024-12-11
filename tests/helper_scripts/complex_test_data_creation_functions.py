import uuid
from typing import Optional

import psycopg
from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient
from database_client.enums import RequestUrgency
from middleware.enums import JurisdictionType
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_advanced_schemas import (
    AgencyInfoPostSchema,
)
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.constants import (
    DATA_REQUESTS_BASE_ENDPOINT,
    AGENCIES_BASE_ENDPOINT,
)
from tests.helper_scripts.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.test_dataclasses import TestDataRequestInfo, TestAgencyInfo


def insert_test_column_permission_data(db_client: DatabaseClient):
    try:
        db_client.execute_raw_sql(
            """
        DO $$
        DECLARE
            column_a_id INT;
            column_b_id INT;
            column_c_id INT;
        BEGIN
            INSERT INTO relation_column (relation, associated_column) VALUES ('test_relation', 'column_a') RETURNING id INTO column_a_id;
            INSERT INTO relation_column (relation, associated_column) VALUES ('test_relation', 'column_b') RETURNING id INTO column_b_id;
            INSERT INTO relation_column (relation, associated_column) VALUES ('test_relation', 'column_c') RETURNING id INTO column_c_id;

            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_a_id, 'STANDARD', 'READ');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_b_id, 'STANDARD', 'READ');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_c_id, 'STANDARD', 'NONE');

            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_a_id, 'OWNER', 'READ');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_b_id, 'OWNER', 'WRITE');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_c_id, 'OWNER', 'NONE');

            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_a_id, 'ADMIN', 'WRITE');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_b_id, 'ADMIN', 'WRITE');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_c_id, 'ADMIN', 'READ');

        END $$;
        """
        )
    except psycopg.errors.UniqueViolation:
        pass  # Already added


def create_agency_entry_for_search_cache(db_client: DatabaseClient) -> str:
    """
    Create an entry in `Agencies` guaranteed to appear in the search cache functionality
    :param db_client:
    :return:
    """
    submitted_name = "TEST SEARCH CACHE NAME"
    db_client._create_entry_in_table(
        table_name="agencies",
        column_value_mappings={
            "submitted_name": submitted_name,
            "name": submitted_name,
            "airtable_uid": uuid.uuid4().hex[:15],
            "count_data_sources": 2000,  # AKA, an absurdly high number to guarantee it's the first result
            "approved": True,
            "homepage_url": None,
            "jurisdiction_type": JurisdictionType.FEDERAL.value,
        },
    )
    return submitted_name


def create_data_source_entry_for_url_duplicate_checking(
    db_client: DatabaseClient,
) -> str:
    """
    Create an entry in `Data Sources` guaranteed to appear in the URL duplicate checking functionality
    :param db_client:
    :return:
    """
    submitted_name = "TEST URL DUPLICATE NAME"
    try:
        db_client._create_entry_in_table(
            table_name="data_sources",
            column_value_mappings={
                "submitted_name": submitted_name,
                "name": submitted_name,
                "rejection_note": "Test rejection note",
                "approval_status": "rejected",
                "source_url": "https://duplicate-checker.com/",
            },
        )
        db_client.execute_raw_sql(
            """
            call refresh_distinct_source_urls();
        """
        )
    except psycopg.errors.UniqueViolation:
        pass  # Already added
    except Exception as e:
        # Rollback
        db_client.connection.rollback()
        raise e


def create_test_data_request(
    flask_client: FlaskClient,
    jwt_authorization_header: dict,
    location_info: Optional[dict] = None,
) -> TestDataRequestInfo:
    submission_notes = uuid.uuid4().hex
    json_to_post = {
        "request_info": {
            "submission_notes": submission_notes,
            "title": get_test_name(),
            "request_urgency": RequestUrgency.INDEFINITE.value,
        }
    }

    if location_info is not None:
        json_to_post["location_infos"] = [location_info]

    json = run_and_validate_request(
        flask_client=flask_client,
        http_method="post",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=jwt_authorization_header,
        json=json_to_post,
    )

    return TestDataRequestInfo(id=json["id"], submission_notes=submission_notes)


def create_test_agency(flask_client: FlaskClient, jwt_authorization_header: dict):
    submitted_name = get_test_name()
    locality_name = get_test_name()
    sample_agency_post_parameters = get_sample_agency_post_parameters(
        submitted_name=submitted_name,
        locality_name=locality_name,
        jurisdiction_type=JurisdictionType.LOCAL,
    )

    json = run_and_validate_request(
        flask_client=flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=jwt_authorization_header,
        json=sample_agency_post_parameters,
    )

    return TestAgencyInfo(id=json["id"], submitted_name=submitted_name)


def get_sample_location_info(locality_name: Optional[str] = None) -> dict:
    if locality_name is None:
        locality_name = get_test_name()
    return {
        "type": "Locality",
        "state_iso": "PA",
        "county_fips": "42003",
        "locality_name": locality_name,
    }


def get_sample_agency_post_parameters(
    submitted_name,
    locality_name,
    jurisdiction_type: JurisdictionType,
    location_info: Optional[dict] = None,
) -> dict:
    """
    Obtains information to be passed to an `/agencies` POST request
    """

    if location_info is None:
        location_info = {
            "type": "Locality",
            "state_iso": "CA",
            "county_fips": "06087",
            "locality_name": locality_name,
        }
    return {
        "agency_info": generate_test_data_from_schema(
            schema=AgencyInfoPostSchema(),
            override={
                "submitted_name": submitted_name,
                "jurisdiction_type": JurisdictionType.LOCAL.value,
            },
        ),
        "location_info": location_info,
    }
