import datetime
import uuid

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from db.client.core import DatabaseClient
from db.enums import (
    ApprovalStatus,
    RequestStatus,
    EventType,
    ExternalAccountTypeEnum,
    RequestUrgency,
)
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.location.locality import Locality
from db.models.implementations.core.log.notification import NotificationLog
from db.models.implementations.core.notification.pending.data_request import (
    DataRequestPendingEventNotification,
)
from db.models.implementations.core.notification.pending.data_source import (
    DataSourcePendingEventNotification,
)
from db.models.implementations.core.notification.queue.data_request import (
    DataRequestUserNotificationQueue,
)
from db.models.implementations.core.notification.queue.data_source import (
    DataSourceUserNotificationQueue,
)
from db.models.implementations.core.user.core import User
from middleware.enums import (
    JurisdictionType,
    Relations,
    AgencyType,
    PermissionsEnum,
    RecordTypes,
)
from middleware.schema_and_dto.dtos.agencies.post import (
    AgencyInfoPostDTO,
    AgenciesPostDTO,
)
from endpoints.instantiations.data_requests_.post.dto import (
    RequestInfoPostDTO,
    DataRequestsPostDTO,
)
from middleware.schema_and_dto.dtos.data_requests.put import (
    DataRequestsPutDTO,
    DataRequestsPutOuterDTO,
)
from middleware.schema_and_dto.dtos.data_sources.post import (
    DataSourcesPostDTO,
    DataSourceEntryDataPostDTO,
)
from middleware.schema_and_dto.dtos.entry_create_update_request import (
    EntryCreateUpdateRequestDTO,
)
from tests.helper_scripts.common_endpoint_calls import CreatedDataSource
from tests.helper_scripts.common_test_data import (
    get_random_number_for_testing,
    get_test_name,
)
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.sqlalchemy_helper import (
    TDCSQLAlchemyHelper,
)
from tests.helper_scripts.helper_functions_simple import get_notification_valid_date
from tests.helper_scripts.test_dataclasses import (
    TestUserDBInfo,
    TestAgencyInfo,
    TestDataRequestInfo,
)


class TestDataCreatorDBClient:
    """
    Creates test data for DatabaseClient tests, using a DatabaseClient
    """

    def __init__(self):
        self.db_client: DatabaseClient = DatabaseClient()
        self.helper = TDCSQLAlchemyHelper()

    def test_name(self, midfix: str = "") -> str:
        return f"TEST_{midfix}_{uuid.uuid4().hex}"

    def test_url(self, midfix: str = "") -> str:
        return f"TEST_{midfix}_{uuid.uuid4().hex}.com"

    def clear_test_data(self) -> None:
        for model in [
            DataRequest,
            Agency,
            Locality,
            DataSource,
            User,
            NotificationLog,
            DataRequestUserNotificationQueue,
            DataSourceUserNotificationQueue,
            DataRequestPendingEventNotification,
            DataSourcePendingEventNotification,
        ]:
            query = delete(model)
            self.db_client.execute(query)

    def county(
        self,
        county_name: str,
        state_iso: str = "PA",
        fips: str | None = None,
    ) -> int:
        state_id = self.helper.get_state_id(state_iso=state_iso)
        if fips is None:
            fips = str(get_random_number_for_testing())
        try:
            return self.db_client.create_county(
                name=county_name, fips=fips, state_id=state_id
            )
        except IntegrityError:
            return self.db_client.get_county_id(
                county_name=county_name, state_id=state_id
            )

    def locality(
        self,
        locality_name: str = "",
        state_iso: str = "PA",
        county_name: str = "Allegheny",
    ) -> int:
        # Create locality and return location id
        county_id = self.helper.get_county_id(
            county_name=county_name, state_iso=state_iso
        )
        if locality_name == "":
            locality_name = self.test_name(locality_name)
        locality_id = self.db_client.create_locality(
            column_value_mappings={
                "name": locality_name,
                "county_id": county_id,
            }
        )
        location_id = self.db_client.get_location_id(
            where_mappings={"locality_id": locality_id}
        )
        return location_id

    def create_valid_notification_event(
        self,
        event_type: EventType = EventType.DATA_SOURCE_APPROVED,
        user_id: int | None = None,
    ) -> int:
        """
        Create valid notification event and return the id of the created event entity
        :event_type:
        :user_id: A user id to follow the given notification event; creates one if none provided
        :return:
        """
        if user_id is None:
            user_id = self.user().id

        vnec = ValidNotificationEventCreator(self)
        if event_type == EventType.DATA_SOURCE_APPROVED:
            return vnec.data_source_approved(user_id)
        elif event_type == EventType.REQUEST_READY_TO_START:
            return vnec.data_request_ready_to_start(user_id)
        elif event_type == EventType.REQUEST_COMPLETE:
            return vnec.data_request_completed(user_id)
        else:
            raise ValueError(f"Invalid event type: {event_type}")

    def user(self) -> TestUserDBInfo:
        email = self.test_name()
        pw_digest = uuid.uuid4().hex

        user_id = self.db_client.create_new_user(email=email, password_digest=pw_digest)
        return TestUserDBInfo(id=user_id, email=email, password_digest=pw_digest)

    def data_source(
        self,
        approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
        record_type: RecordTypes | None = RecordTypes.ACCIDENT_REPORTS,
        source_url: str | None = None,
    ) -> CreatedDataSource:
        dto = DataSourcesPostDTO(
            entry_data=DataSourceEntryDataPostDTO(
                name=self.test_name(),
                source_url=source_url or self.test_url(),
                agency_supplied=True,
                approval_status=approval_status,
                record_type_name=record_type,
            )
        )

        id = self.db_client.add_data_source_v2(dto)
        return CreatedDataSource(
            id=id, name=dto.entry_data.name, url=dto.entry_data.source_url
        )

    def link_data_request_to_location(self, data_request_id: int, location_id: int):
        self.db_client.create_request_location_relation(
            column_value_mappings={
                "data_request_id": data_request_id,
                "location_id": location_id,
            }
        )

    def link_data_source_to_agency(self, data_source_id: int, agency_id: int):
        self.db_client.create_data_source_agency_relation(
            column_value_mappings={
                "data_source_id": data_source_id,
                "agency_id": agency_id,
            }
        )

    def update_data_source(self, data_source_id: int, column_value_mappings: dict):
        self.db_client.update_data_source(
            entry_id=data_source_id, column_edit_mappings=column_value_mappings
        )

    def agency(
        self, location_id: int | None = None, **additional_column_value_mappings
    ) -> TestAgencyInfo:
        agency_name = self.test_name()
        agency_info = AgencyInfoPostDTO(
            name=agency_name,
            agency_type=AgencyType.POLICE,
            jurisdiction_type=JurisdictionType.FEDERAL,
        )
        for key, value in additional_column_value_mappings.items():
            setattr(agency_info, key, value)

        dto = AgenciesPostDTO(
            agency_info=agency_info,
            location_ids=[location_id] if location_id is not None else None,
        )

        agency_id = self.db_client.create_agency(dto=dto)
        return TestAgencyInfo(id=agency_id, submitted_name=agency_name)

    def update_agency(self, agency_id: int, column_value_mappings: dict):
        self.db_client.update_agency(
            entry_id=agency_id, column_value_mappings=column_value_mappings
        )

    def data_request(
        self,
        user_id: int | None = None,
        request_status: RequestStatus | None = RequestStatus.INTAKE,
        record_type: RecordTypes | None = None,
        location_ids: list[int] | None = None,
    ) -> TestDataRequestInfo:
        if record_type is None:
            record_type_as_list = []
        else:
            record_type_as_list = [record_type]
        if user_id is None:
            user_id = self.user().id

        submission_notes = self.test_name()
        dto = DataRequestsPostDTO(
            request_info=RequestInfoPostDTO(
                title=get_test_name(),
                submission_notes=submission_notes,
                request_status=request_status,
                request_urgency=RequestUrgency.INDEFINITE,
                record_types_required=record_type_as_list,
            ),
            location_ids=location_ids
        )
        data_request_id = self.db_client.create_data_request_v2(
            dto=dto, user_id=user_id
        )
        return TestDataRequestInfo(
            id=data_request_id, submission_notes=submission_notes
        )

    def user_follow_location(
        self,
        user_id: int,
        location_id: int,
        record_types: list[RecordTypes] | None = None,
    ) -> None:
        self.db_client.create_followed_search(
            user_id=user_id, location_id=location_id, record_types=record_types
        )

    def link_data_request_to_data_source(
        self, data_request_id: int, data_source_id: str
    ):
        self.db_client.create_request_source_relation(
            column_value_mappings={
                "data_source_id": data_source_id,
                "request_id": data_request_id,
            }
        )

    def link_fake_github_to_user(self, user_id: int) -> int:
        fake_id = get_random_number_for_testing()
        self.db_client.link_external_account(
            user_id=str(user_id),
            external_account_id=fake_id,
            external_account_type=ExternalAccountTypeEnum.GITHUB,
        )
        return fake_id

    def create_states(self):
        states = [
            ["AL", "Alabama"],
            ["AK", "Alaska"],
            ["AZ", "Arizona"],
            ["AR", "Arkansas"],
            ["CA", "California"],
            ["CZ", "Canal Zone"],
            ["CO", "Colorado"],
            ["CT", "Connecticut"],
            ["DE", "Delaware"],
            ["DC", "District of Columbia"],
            ["FL", "Florida"],
            ["GA", "Georgia"],
            ["GU", "Guam"],
            ["HI", "Hawaii"],
            ["ID", "Idaho"],
            ["IL", "Illinois"],
            ["IN", "Indiana"],
            ["IA", "Iowa"],
            ["KS", "Kansas"],
            ["KY", "Kentucky"],
            ["LA", "Louisiana"],
            ["ME", "Maine"],
            ["MD", "Maryland"],
            ["MA", "Massachusetts"],
            ["MI", "Michigan"],
            ["MN", "Minnesota"],
            ["MS", "Mississippi"],
            ["MO", "Missouri"],
            ["MT", "Montana"],
            ["NE", "Nebraska"],
            ["NV", "Nevada"],
            ["NH", "New Hampshire"],
            ["NJ", "New Jersey"],
            ["NM", "New Mexico"],
            ["NY", "New York"],
            ["NC", "North Carolina"],
            ["ND", "North Dakota"],
            ["OH", "Ohio"],
            ["OK", "Oklahoma"],
            ["OR", "Oregon"],
            ["PA", "Pennsylvania"],
            ["PR", "Puerto Rico"],
            ["RI", "Rhode Island"],
            ["SC", "South Carolina"],
            ["SD", "South Dakota"],
            ["TN", "Tennessee"],
            ["TX", "Texas"],
            ["UT", "Utah"],
            ["VT", "Vermont"],
            ["VI", "Virgin Islands"],
            ["VA", "Virginia"],
            ["WA", "Washington"],
            ["WV", "West Virginia"],
            ["WI", "Wisconsin"],
            ["WY", "Wyoming"],
        ]
        for state_abbr, state_name in states:
            try:
                self.db_client._create_entry_in_table(
                    table_name=Relations.US_STATES.value,
                    column_value_mappings={
                        "state_name": state_name,
                        "state_iso": state_abbr,
                    },
                )
            except IntegrityError:
                # Already exists. Keep going
                pass

    def notification_log(self) -> datetime.datetime:
        dt = datetime.datetime.now() - datetime.timedelta(weeks=4)
        self.db_client.add_to_notification_log(user_count=0, dt=dt)
        return dt


class ValidNotificationEventCreatorV2:
    """Creates events designed to be picked up by the notification service."""

    def __init__(self, tdc: TestDataCreatorDBClient):
        self.tdc = tdc
        self.notification_valid_date = get_notification_valid_date()
        self.user_id = self.tdc.user().id

    def data_source_approved(self, record_type: RecordTypes, location_id: int) -> int:
        """Create approved data source with record type and link to agency with location"""
        agency_info = self.tdc.agency(location_id)
        ds_info = self.tdc.data_source()
        self.tdc.link_data_source_to_agency(
            data_source_id=ds_info.id, agency_id=agency_info.id
        )
        self.tdc.db_client.update_data_source_v2(
            dto=EntryCreateUpdateRequestDTO(
                entry_data={
                    "approval_status_updated_at": self.notification_valid_date,
                    "record_type_name": record_type.value,
                }
            ),
            user_id=self.user_id,
            data_source_id=ds_info.id,
            permissions=[PermissionsEnum.DB_WRITE],
        )
        return ds_info.id

    def create_data_request(
        self, request_status: RequestStatus, record_type: RecordTypes, location_id: int
    ) -> int:
        """Create data request of given request status and record type and link to location"""
        dr_info = self.tdc.data_request()
        self.tdc.db_client.update_data_request_v2(
            data_request_id=dr_info.id,
            dto=DataRequestsPutOuterDTO(
                entry_data=DataRequestsPutDTO(
                    request_status=request_status,
                    record_types_required=[record_type],
                )
            ),
            bypass_permissions=True,
        )
        self.tdc.db_client.create_request_location_relation(
            column_value_mappings={
                "data_request_id": dr_info.id,
                "location_id": location_id,
            }
        )
        self.tdc.db_client.update_data_request(
            entry_id=dr_info.id,
            column_edit_mappings={
                "date_status_last_changed": self.notification_valid_date
            },
        )
        return dr_info.id


class ValidNotificationEventCreator:
    def __init__(self, tdc: TestDataCreatorDBClient):
        self.tdc = tdc
        self.notification_valid_date = get_notification_valid_date()

    def data_source_approved(self, user_id: int) -> int:
        locality_location_id = self.tdc.locality()
        agency_info = self.tdc.agency(locality_location_id)
        ds_info = self.tdc.data_source()
        self.tdc.link_data_source_to_agency(
            data_source_id=ds_info.id, agency_id=agency_info.id
        )
        self.tdc.db_client.update_data_source_v2(
            dto=EntryCreateUpdateRequestDTO(
                entry_data={"approval_status_updated_at": self.notification_valid_date}
            ),
            user_id=user_id,
            data_source_id=ds_info.id,
            permissions=[PermissionsEnum.DB_WRITE],
        )
        self.tdc.user_follow_location(user_id=user_id, location_id=locality_location_id)
        return ds_info.id

    def _create_data_request(self, request_status: RequestStatus, user_id: int) -> int:
        dr_info = self.tdc.data_request()
        locality_location_id = self.tdc.locality()
        self.tdc.db_client.update_data_request_v2(
            data_request_id=dr_info.id,
            dto=DataRequestsPutOuterDTO(
                entry_data=DataRequestsPutDTO(
                    request_status=request_status,
                )
            ),
            bypass_permissions=True,
        )
        self.tdc.db_client.create_request_location_relation(
            column_value_mappings={
                "data_request_id": dr_info.id,
                "location_id": locality_location_id,
            }
        )
        self.tdc.db_client.update_data_request(
            entry_id=dr_info.id,
            column_edit_mappings={
                "date_status_last_changed": self.notification_valid_date
            },
        )
        self.tdc.user_follow_location(user_id=user_id, location_id=locality_location_id)
        return dr_info.id

    def data_request_ready_to_start(self, user_id: int):
        return self._create_data_request(RequestStatus.READY_TO_START, user_id)

    def data_request_completed(self, user_id: int):
        return self._create_data_request(RequestStatus.COMPLETE, user_id)
