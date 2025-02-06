from typing import Optional

from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient
from database_client.enums import RequestStatus
from middleware.enums import JurisdictionType, PermissionsEnum
from tests.helper_scripts.common_endpoint_calls import CreatedDataSource
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.complex_test_data_creation_functions import (
    create_test_data_request,
    get_sample_agency_post_parameters,
)
from tests.helper_scripts.constants import (
    DATA_REQUESTS_BY_ID_ENDPOINT,
    AGENCIES_BASE_ENDPOINT,
    AGENCIES_BY_ID_ENDPOINT,
    DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT,
    DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT,
)
from tests.helper_scripts.helper_classes.RequestValidator import RequestValidator
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import (
    TestDataCreatorDBClient,
)
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions_complex import (
    create_admin_test_user_setup,
    create_test_user_setup,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.test_dataclasses import TestDataRequestInfo, TestAgencyInfo


class TestDataCreatorFlask:
    """
    Creates test data for Flask integration tests, using a FlaskClient
    """

    def __init__(self, flask_client: FlaskClient):
        self.flask_client = flask_client
        self.tdcdb = TestDataCreatorDBClient()
        self.request_validator = RequestValidator(flask_client)
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
        submitted_name = get_test_name()
        json = self.request_validator.create_data_source(
            headers=self.get_admin_tus().jwt_authorization_header,
            submitted_name=submitted_name,
        )

        return CreatedDataSource(
            id=json["id"],
            name=submitted_name,
        )

    def clear_test_data(self):
        tdc_db = TestDataCreatorDBClient()
        tdc_db.clear_test_data()
        # Recreate admin user
        self.admin_tus = create_admin_test_user_setup(self.flask_client)

    def data_request(
        self,
        user_tus: Optional[TestUserSetup] = None,
        location_ids: Optional[list[int]] = None,
    ) -> TestDataRequestInfo:
        if user_tus is None:
            user_tus = self.get_admin_tus()
        tdr = create_test_data_request(
            flask_client=self.flask_client,
            jwt_authorization_header=user_tus.jwt_authorization_header,
        )
        if location_ids is not None:
            for location_id in location_ids:
                self.request_validator.link_data_request_with_location(
                    data_request_id=tdr.id,
                    location_id=location_id,
                    headers=self.get_admin_tus().jwt_authorization_header,
                )

        return tdr

    def update_data_request_status(self, data_request_id: int, status: RequestStatus):
        run_and_validate_request(
            flask_client=self.flask_client,
            http_method="put",
            endpoint=DATA_REQUESTS_BY_ID_ENDPOINT.format(
                data_request_id=data_request_id
            ),
            headers=self.get_admin_tus().jwt_authorization_header,
            json={"request_status": status.value},
        )

    def agency(
        self,
        location_info: Optional[dict] = None,
        agency_name: str = "",
        add_test_name: bool = True,
    ) -> TestAgencyInfo:
        if add_test_name and agency_name == "":
            submitted_name = self.tdcdb.test_name(agency_name)
        else:
            submitted_name = agency_name
        locality_name = self.tdcdb.test_name()
        sample_agency_post_parameters = get_sample_agency_post_parameters(
            name=submitted_name,
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

    def refresh_typeahead_agencies(self):
        self.db_client.execute_raw_sql("CALL refresh_typeahead_agencies();")

    def update_agency(self, agency_id: int, data_to_update: dict):
        run_and_validate_request(
            flask_client=self.flask_client,
            http_method="put",
            endpoint=AGENCIES_BY_ID_ENDPOINT.format(agency_id=agency_id),
            headers=self.get_admin_tus().jwt_authorization_header,
            json=data_to_update,
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

    def standard_user(self) -> TestUserSetup:
        """
        Creates a user with no special permissions.
        :return:
        """
        return create_test_user_setup(self.flask_client)

    def notifications_user(self) -> TestUserSetup:
        """
        Creates a user with notifications permissions.
        :return:
        """
        return create_test_user_setup(
            self.flask_client, permissions=[PermissionsEnum.NOTIFICATIONS]
        )

    def locality(
        self,
        locality_name: str = "",
        state_iso: str = "PA",
        county_name: str = "Allegheny",
    ):
        return self.tdcdb.locality(
            locality_name=locality_name, state_iso=state_iso, county_name=county_name
        )

    def add_permission(self, user_email: str, permission: PermissionsEnum):
        self.request_validator.update_permissions(
            user_email=user_email,
            headers=self.get_admin_tus().jwt_authorization_header,
            action="add",
            permission=permission.value,
        )

        # TODO: Create a tuple providing all 4 id's -- for the user, the data_source, the agency, and the data_request
