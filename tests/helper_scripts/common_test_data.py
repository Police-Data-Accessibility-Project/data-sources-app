import random
import uuid
from typing import Optional

import psycopg
from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient
from database_client.enums import RequestUrgency, RequestStatus
from middleware.enums import JurisdictionType
from tests.helper_scripts.common_endpoint_calls import (
    create_data_source_with_endpoint,
    CreatedDataSource,
)
from tests.helper_scripts.constants import (
    DATA_REQUESTS_BASE_ENDPOINT,
    AGENCIES_BASE_ENDPOINT,
    DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT, DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT,
    DATA_REQUESTS_BY_ID_ENDPOINT, AGENCIES_BY_ID_ENDPOINT,
)
from tests.helper_scripts.helper_classes.EndpointCaller import EndpointCaller
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions import (
    create_test_user_setup,
    create_admin_test_user_setup,
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
    flask_client: FlaskClient, jwt_authorization_header: dict, location_info: Optional[dict] = None
) -> TestDataRequestInfo:
    submission_notes = uuid.uuid4().hex
    json_to_post = {
        "request_info": {
            "submission_notes": submission_notes,
            "title": uuid.uuid4().hex,
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
    submitted_name = uuid.uuid4().hex
    locality_name = uuid.uuid4().hex
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


class TestDataCreatorFlask:
    """
    Creates test data for Flask integration tests, using a FlaskClient
    """

    def __init__(self, flask_client: FlaskClient):
        self.flask_client = flask_client
        self.endpoint_caller = EndpointCaller(flask_client)
        self.db_client = DatabaseClient()
        self.admin_tus: Optional[TestUserSetup] = None

    def get_admin_tus(self) -> TestUserSetup:
        """
        Lazy load the TestUserSetup object for the admin user.
        :return:
        """
        if self.admin_tus is None:
            self.admin_tus = create_admin_test_user_setup(self.flask_client)
        return self.admin_tus

    def data_source(self, location_info: Optional[dict] = None) -> CreatedDataSource:
        ds_info = create_data_source_with_endpoint(
            flask_client=self.flask_client,
            jwt_authorization_header=self.get_admin_tus().jwt_authorization_header,
        )

        if location_info is not None:
            run_and_validate_request(
                flask_client=self.flask_client,
                http_method="post",
                endpoint=DATA_SOURCES_POST_UPDATE_LOCATION_ENDPOINT.format(
                    data_source_id=ds_info.id
                ),
                headers=self.get_admin_tus().jwt_authorization_header,
                json=location_info,
            )

    def data_request(self, user_tus: Optional[TestUserSetup] = None, location_info: Optional[dict] = None) -> TestDataRequestInfo:
        if user_tus is None:
            user_tus = self.get_admin_tus()
        return create_test_data_request(
            flask_client=self.flask_client,
            jwt_authorization_header=user_tus.jwt_authorization_header,
        )

    def update_data_request_status(self, data_request_id: int, status: RequestStatus):
        run_and_validate_request(
            flask_client=self.flask_client,
            http_method="put",
            endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(data_request_id=data_request_id),
            headers=self.get_admin_tus().jwt_authorization_header,
            json={"request_status": status.value},
        )

    def agency(self, location_info: Optional[dict] = None) -> TestAgencyInfo:
        submitted_name = uuid.uuid4().hex
        locality_name = uuid.uuid4().hex
        sample_agency_post_parameters = get_sample_agency_post_parameters(
            submitted_name=submitted_name,
            locality_name=locality_name,
            jurisdiction_type=JurisdictionType.LOCAL,
            location_info=location_info,
        )

        json = run_and_validate_request(
            flask_client=self.flask_client,
            http_method="post",
            endpoint=AGENCIES_BASE_ENDPOINT,
            headers=self.get_admin_tus().jwt_authorization_header,
            json=sample_agency_post_parameters,
        )

        return TestAgencyInfo(id=json["id"], submitted_name=submitted_name)

    def update_agency(self, agency_id: int, data_to_update: dict):
        run_and_validate_request(
            flask_client=self.flask_client,
            http_method="put",
            endpoint=AGENCIES_BY_ID_ENDPOINT.format(agency_id=agency_id),
            headers=self.get_admin_tus().jwt_authorization_header,
            json=data_to_update
        )

    def link_data_source_to_agency(self, data_source_id, agency_id):
        run_and_validate_request(
            flask_client=self.flask_client,
            http_method="post",
            endpoint=DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT.format(
                data_source_id=data_source_id, agency_id=agency_id
            ),
            headers=self.get_admin_tus().jwt_authorization_header,
        )

    def link_data_request_to_data_source(self, data_source_id, data_request_id):
        run_and_validate_request(
            flask_client=self.flask_client,
            http_method="post",
            endpoint=DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT.format(
                data_request_id=data_request_id, source_id=data_source_id
            ),
            headers=self.get_admin_tus().jwt_authorization_header,
        )

    def link_data_source_to_agency(self, data_source_id, agency_id):
        raise NotImplementedError()

    def standard_user(self) -> TestUserSetup:
        """
        Creates a user with no special permissions.
        :return:
        """
        return create_test_user_setup(self.flask_client)

    def select_only_complex_linked_resources(self):
        """
        Create the following:
        * An agency
        * A data source linked to that agency
        * A standard user
        * A data request linked to that data source, created by that user
        This data source is meant to persist and not be edited, to reduce setup time.
        :return:
        """
        agency_info = self.agency()
        # TODO: Link agency with data source
        raise NotImplementedError()
        data_source_info = self.data_source()
        standard_user_tus = self.standard_user()
        data_request_info = self.data_request(standard_user_tus)

        self.link_data_request_to_data_source(
            data_source_id=data_source_info.id, data_request_id=data_request_info.id
        )

        # TODO: Create a tuple providing all 4 id's -- for the user, the data_source, the agency, and the data_request


def get_sample_agency_post_parameters(
    submitted_name,
    locality_name,
    jurisdiction_type: JurisdictionType,
    location_info: Optional[dict] = None
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
        "agency_info": {
            "submitted_name": submitted_name,
            "jurisdiction_type": jurisdiction_type.value,
        },
        "location_info": location_info,
    }


def get_random_number_for_testing():
    number = random.randint(1, 999999999)
    return number
