from typing import Optional

from flask.testing import FlaskClient

from db.client.core import DatabaseClient
from db.enums import RequestStatus, ApprovalStatus
from middleware.enums import JurisdictionType, PermissionsEnum, AgencyType, RecordTypes
from middleware.schema_and_dto.schemas.agencies.info.post import (
    AgencyInfoPostSchema,
)
from tests.helper_scripts.common_endpoint_calls import CreatedDataSource
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.constants import (
    AGENCIES_BASE_ENDPOINT,
    DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT,
    DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT,
)
from tests.helper_scripts.helper_classes.RequestValidator import RequestValidator
from tests.helper_scripts.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
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
        submitted_name = get_test_name()
        url = self.tdcdb.test_url()
        json = self.request_validator.create_data_source(
            headers=self.get_admin_tus().jwt_authorization_header,
            source_url=url,
            name=submitted_name,
            record_type_name=RecordTypes.ARREST_RECORDS.value,
        )

        return CreatedDataSource(id=json["id"], name=submitted_name, url=url)

    def clear_test_data(self):
        tdc_db = TestDataCreatorDBClient()
        tdc_db.clear_test_data()
        # Recreate admin user
        self.admin_tus = create_admin_test_user_setup(self.flask_client)

    def data_request(
        self,
        user_id: int | None = None,
        request_status: RequestStatus | None = RequestStatus.INTAKE,
        record_type: RecordTypes | None = None,
        location_ids: list[int] | None = None,
    ) -> TestDataRequestInfo:
        return self.tdcdb.data_request(
            user_id=user_id,
            request_status=request_status,
            record_type=record_type,
            location_ids=location_ids,
        )

    def get_sample_agency_post_parameters(
        self,
        name,
        locality_name,
        jurisdiction_type: JurisdictionType,
        location_ids: Optional[list[dict]] = None,
        approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
    ) -> dict:
        d = {
            "agency_info": generate_test_data_from_schema(
                schema=AgencyInfoPostSchema(),
                override={
                    "name": name,
                    "jurisdiction_type": jurisdiction_type.value,
                    "agency_type": AgencyType.POLICE.value,
                    "approval_status": approval_status.value,
                },
            ),
        }

        if location_ids is None and jurisdiction_type != JurisdictionType.FEDERAL:
            location_id = self.locality(
                locality_name=locality_name,
            )
            location_ids = [location_id]

        if location_ids is not None:
            d["location_ids"] = location_ids

        return d

    def agency(
        self,
        location_ids: Optional[list[dict]] = None,
        agency_name: str = "",
        add_test_name: bool = True,
        approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
        jurisdiction_type: JurisdictionType = JurisdictionType.LOCAL,
    ) -> TestAgencyInfo:
        if add_test_name and agency_name == "":
            submitted_name = self.tdcdb.test_name(agency_name)
        else:
            submitted_name = agency_name
        locality_name = self.tdcdb.test_name()
        sample_agency_post_parameters = self.get_sample_agency_post_parameters(
            name=submitted_name,
            locality_name=locality_name,
            jurisdiction_type=jurisdiction_type,
            location_ids=location_ids,
            approval_status=approval_status,
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

    def refresh_typeahead_locations(self):
        self.db_client.execute_raw_sql("CALL refresh_typeahead_locations();")

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
