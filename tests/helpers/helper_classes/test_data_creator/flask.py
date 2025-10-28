from typing import Optional

from flask.testing import FlaskClient

from db.client.core import DatabaseClient
from db.enums import RequestStatus
from middleware.enums import JurisdictionType, PermissionsEnum, RecordTypesEnum
from tests.helpers.common_endpoint_calls import CreatedDataSource
from tests.helpers.constants import (
    DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT,
)
from tests.helpers.helper_classes.RequestValidator import RequestValidator
from tests.helpers.helper_classes.TestUserSetup import TestUserSetup
from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.helpers.helper_functions_complex import (
    create_admin_test_user_setup,
    create_test_user_setup,
)
from tests.helpers.run_and_validate_request import run_and_validate_request
from tests.helpers.test_dataclasses import TestDataRequestInfo, TestAgencyInfo


class TestDataCreatorFlask:
    """
    Creates test data for Flask integration tests, using a FlaskClient
    """

    def __init__(self, flask_client: FlaskClient):
        self.flask_client = flask_client
        self.tdcdb: TestDataCreatorDBClient = TestDataCreatorDBClient()
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
        url = self.tdcdb.test_url()
        cdc: CreatedDataSource = self.tdcdb.data_source(
            source_url=url,
        )
        return cdc

    def clear_test_data(self):
        tdc_db = TestDataCreatorDBClient()
        tdc_db.clear_test_data()
        # Recreate admin user
        self.admin_tus = create_admin_test_user_setup(self.flask_client)

    def data_request(
        self,
        user_id: int | None = None,
        request_status: RequestStatus | None = RequestStatus.INTAKE,
        record_type: RecordTypesEnum | None = None,
        location_ids: list[int] | None = None,
    ) -> TestDataRequestInfo:
        return self.tdcdb.data_request(
            user_id=user_id,
            request_status=request_status,
            record_type=record_type,
            location_ids=location_ids,
        )

    def agency(
        self,
        location_ids: Optional[list[dict]] = None,
        agency_name: str = "",
        add_test_name: bool = True,
        jurisdiction_type: JurisdictionType = JurisdictionType.LOCAL,
    ) -> TestAgencyInfo:
        if add_test_name and agency_name == "":
            submitted_name = self.tdcdb.test_name(agency_name)
        else:
            submitted_name = agency_name

        test_agency_info: TestAgencyInfo = self.tdcdb.agency(
            name=submitted_name,
            jurisdiction_type=jurisdiction_type,
        )

        if location_ids is not None:
            for location_id in location_ids:
                self.tdcdb.db_client.add_location_to_agency(
                    location_id=location_id,
                    agency_id=test_agency_info.id,
                )

        return TestAgencyInfo(id=test_agency_info.id, submitted_name=submitted_name)

    def refresh_typeahead_agencies(self):
        self.db_client.execute_raw_sql("CALL refresh_typeahead_agencies();")

    def refresh_typeahead_locations(self):
        self.db_client.execute_raw_sql("CALL refresh_typeahead_locations();")

    def link_data_source_to_agency(self, data_source_id: int, agency_id: int):
        self.tdcdb.link_data_source_to_agency(
            data_source_id=data_source_id,
            agency_id=agency_id,
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

    def user_with_permissions(
        self, permissions: list[PermissionsEnum]
    ) -> TestUserSetup:
        return create_test_user_setup(self.flask_client, permissions=permissions)

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
