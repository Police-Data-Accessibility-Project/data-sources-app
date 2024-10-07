import uuid
from collections import namedtuple
from typing import Optional

import psycopg
from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient
from middleware.enums import JurisdictionType
from tests.helper_scripts.common_endpoint_calls import create_data_source_with_endpoint, CreatedDataSource
from tests.helper_scripts.constants import DATA_REQUESTS_BASE_ENDPOINT, AGENCIES_BASE_ENDPOINT, \
    DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions import create_test_user_setup, create_admin_test_user_setup
from tests.helper_scripts.run_and_validate_request import run_and_validate_request

TestUserDBInfo = namedtuple("TestUserDBInfo", ["id", "email", "password_digest"])

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
                "airtable_uid": "TEST_URL_DUPLICATE_SOURCE_ID",
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


TestDataRequestInfo = namedtuple("TestDataRequestInfo", ["id", "submission_notes"])


def create_test_data_request(
    flask_client: FlaskClient, jwt_authorization_header: dict
) -> TestDataRequestInfo:
    submission_notes = uuid.uuid4().hex
    json = run_and_validate_request(
        flask_client=flask_client,
        http_method="post",
        endpoint=DATA_REQUESTS_BASE_ENDPOINT,
        headers=jwt_authorization_header,
        json={"entry_data": {"submission_notes": submission_notes}},
    )

    return TestDataRequestInfo(id=json["id"], submission_notes=submission_notes)

TestAgencyInfo = namedtuple("TestAgencyInfo", ["id", "submitted_name"])

def create_test_agency(
        flask_client: FlaskClient,
        jwt_authorization_header: dict
):
    submitted_name = uuid.uuid4().hex
    locality_name = uuid.uuid4().hex
    sample_agency_post_parameters = get_sample_agency_post_parameters(
        submitted_name=submitted_name,
        locality_name=locality_name,
        jurisdiction_type=JurisdictionType.LOCAL
    )

    json = run_and_validate_request(
        flask_client=flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=jwt_authorization_header,
        json=sample_agency_post_parameters
    )

    return TestAgencyInfo(id=json["id"], submitted_name=submitted_name)

class TestDataCreatorFlask:
    """
    Creates test data for Flask integration tests, using a FlaskClient
    """

    def __init__(self, flask_client: FlaskClient):
        self.flask_client = flask_client
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

    def data_source(self) -> CreatedDataSource:
        return create_data_source_with_endpoint(
            flask_client=self.flask_client,
            jwt_authorization_header=self.get_admin_tus().jwt_authorization_header,
        )

    def data_request(self, user_tus: TestUserSetup):
        return create_test_data_request(
            flask_client=self.flask_client,
            jwt_authorization_header=user_tus.jwt_authorization_header
        )

    def agency(self) -> TestAgencyInfo:
        return create_test_agency(
            flask_client=self.flask_client,
            jwt_authorization_header=self.get_admin_tus().jwt_authorization_header
        )

    def link_data_request_to_data_source(self, data_source_id, data_request_id):
        run_and_validate_request(
            flask_client=self.flask_client,
            http_method="post",
            endpoint=DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT.format(
                data_request_id=data_request_id,
                source_id=data_source_id
            ),
            headers=self.get_admin_tus().jwt_authorization_header
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
            data_source_id=data_source_info.id,
            data_request_id=data_request_info.id
        )

        # TODO: Create a tuple providing all 4 id's -- for the user, the data_source, the agency, and the data_request




def get_sample_agency_post_parameters(
    submitted_name, locality_name, jurisdiction_type: JurisdictionType
) -> dict:
    """
    Obtains information to be passed to an `/agencies` POST request
    """
    return {
        "agency_info": {
            "submitted_name": submitted_name,
            "airtable_uid": uuid.uuid4().hex,
            "jurisdiction_type": jurisdiction_type.value,
        },
        "location_info": {
            "type": "Locality",
            "state_iso": "CA",
            "county_fips": "06087",
            "locality_name": locality_name,
        },
    }

class TestDataCreatorDBClient:
    """
    Creates test data for DatabaseClient tests, using a DatabaseClient
    """
    def __init__(self):
        self.db_client = DatabaseClient()

    def user(self) -> TestUserDBInfo:
        email = uuid.uuid4().hex
        pw_digest = uuid.uuid4().hex

        user_id = self.db_client.create_new_user(
            email=email,
            password_digest=pw_digest
        )
        return TestUserDBInfo(
            id=user_id,
            email=email,
            password_digest=pw_digest
        )

    def data_source(self) -> CreatedDataSource:
        cds = CreatedDataSource(
            id=uuid.uuid4().hex,
            name=uuid.uuid4().hex
        )
        source_column_value_mapping = {
            "airtable_uid": cds.id,
            "name": cds.name,
        }
        self.db_client.add_new_data_source(
            column_value_mappings=source_column_value_mapping
        )
        return cds

    def data_request(self, user_id: Optional[int] = None) -> TestDataRequestInfo:
        if user_id is None:
            user_id = self.user().id

        submission_notes = uuid.uuid4().hex
        data_request_id = self.db_client.create_data_request(
            column_value_mappings={
                "submission_notes": submission_notes,
                "creator_user_id": user_id
            }
        )
        return TestDataRequestInfo(
            id=data_request_id,
            submission_notes=submission_notes
        )

    def link_data_request_to_data_source(self, data_request_id: int, data_source_id: str):
        self.db_client.create_request_source_relation(
            column_value_mappings={
                "source_id": data_source_id,
                "request_id": data_request_id
            }
        )

