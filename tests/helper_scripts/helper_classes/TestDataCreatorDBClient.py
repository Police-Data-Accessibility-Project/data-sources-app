import uuid
from typing import Optional

from sqlalchemy import delete, select, and_
from sqlalchemy.exc import IntegrityError

from database_client.database_client import DatabaseClient
from database_client.enums import (
    ApprovalStatus,
    RequestStatus,
    EventType,
    ExternalAccountTypeEnum,
)
from database_client.models import SQL_ALCHEMY_TABLE_REFERENCE
from middleware.enums import JurisdictionType, Relations, AgencyType
from middleware.schema_and_dto_logic.primary_resource_dtos.agencies_dtos import (
    AgenciesPostDTO,
    AgencyInfoPostDTO,
)
from tests.helper_scripts.common_endpoint_calls import CreatedDataSource
from tests.helper_scripts.common_test_data import (
    get_random_number_for_testing,
    get_test_name,
)
from tests.helper_scripts.helper_functions_simple import get_notification_valid_date
from tests.helper_scripts.test_dataclasses import (
    TestUserDBInfo,
    TestAgencyInfo,
    TestDataRequestInfo,
)


class TDCSQLAlchemyHelper:

    def __init__(self):
        self.db_client = DatabaseClient()

    def delete_like(
        self,
        table_name: str,
        like_column_name: str,
        like_text: str,
    ):
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        column = getattr(table, like_column_name)
        query = delete(table).where(column.like(like_text))
        self.db_client.execute_sqlalchemy(lambda: query)

    def delete_from_table(
        self,
        table_name: str,
    ):
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        query = delete(table)
        self.db_client.execute_sqlalchemy(lambda: query)

    def delete_test_like(
        self,
        table_name: str,
        like_column_name: str,
    ):
        self.delete_like(
            table_name=table_name, like_column_name=like_column_name, like_text="TEST_%"
        )

    def get_county_id(self, county_name: str, state_iso: str = "PA") -> int:
        state_id = self.get_state_id(state_iso=state_iso)
        table = SQL_ALCHEMY_TABLE_REFERENCE[Relations.COUNTIES.value]
        state_id_column = getattr(table, "state_id")
        county_name_column = getattr(table, "name")
        county_id_column = getattr(table, "id")
        query = select(county_id_column).where(
            and_(county_name_column == county_name, state_id_column == state_id)
        )
        result = self.db_client.execute_sqlalchemy(lambda: query)
        return [row[0] for row in result][0]

    def get_state_id(self, state_iso: str) -> int:
        table = SQL_ALCHEMY_TABLE_REFERENCE[Relations.US_STATES.value]
        column_name = getattr(table, "state_iso")
        column_id = getattr(table, "id")
        query = select(column_id).where(column_name == state_iso)
        result = self.db_client.execute_sqlalchemy(lambda: query)
        results = [result[0] for result in result]
        if len(results) == 0:
            raise Exception(f"Could not find state with iso {state_iso}")
        return results[0]

    def clear_user_notification_queue(self):
        table = SQL_ALCHEMY_TABLE_REFERENCE[Relations.USER_NOTIFICATION_QUEUE.value]
        query = delete(table)
        self.db_client.execute_sqlalchemy(lambda: query)


class TestDataCreatorDBClient:
    """
    Creates test data for DatabaseClient tests, using a DatabaseClient
    """

    def __init__(self):
        self.db_client: DatabaseClient = DatabaseClient()
        self.helper = TDCSQLAlchemyHelper()

    def test_name(self, midfix: str = ""):
        return f"TEST_{midfix}_{uuid.uuid4().hex}"

    def test_url(self, midfix: str = ""):
        return f"TEST_{midfix}_{uuid.uuid4().hex}.com"

    def clear_test_data(self):
        # Remove test data from data request
        self.helper.delete_test_like(
            table_name=Relations.DATA_REQUESTS.value,
            like_column_name="title",
        )
        self.helper.delete_test_like(
            table_name=Relations.DATA_REQUESTS.value,
            like_column_name="submission_notes",
        )
        # Remove test data from agency
        self.helper.delete_from_table(
            table_name=Relations.AGENCIES.value,
        )
        self.helper.delete_test_like(
            table_name=Relations.AGENCIES.value,
            like_column_name="name",
        )
        # Remove test data from locality
        self.helper.delete_test_like(
            table_name=Relations.LOCALITIES.value,
            like_column_name="name",
        )

        # Remove test data from data source
        self.helper.delete_test_like(
            table_name=Relations.DATA_SOURCES.value,
            like_column_name="name",
        )

        # Remove test data from user
        self.helper.delete_test_like(
            table_name=Relations.USERS.value,
            like_column_name="email",
        )

        self.helper.clear_user_notification_queue()

    def county(
        self,
        county_name: str,
        state_iso: str = "PA",
        fips: Optional[str] = None,
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
            column_value_mappings={"name": locality_name, "county_id": county_id}
        )
        location_id = self.db_client.get_location_id(
            where_mappings={"locality_id": locality_id}
        )
        return location_id

    def create_valid_notification_event(
        self,
        event_type: EventType = EventType.DATA_SOURCE_APPROVED,
        user_id: Optional[int] = None,
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
        record_type_id: int = 1,
        **additional_column_values,
    ) -> CreatedDataSource:
        cds = CreatedDataSource(id=uuid.uuid4().hex, name=self.test_name())
        source_column_value_mapping = {
            "name": cds.name,
            "source_url": self.test_url(),
            "agency_supplied": True,
            "record_type_id": record_type_id,
        }
        source_column_value_mapping.update(additional_column_values)
        if approval_status is not None:
            source_column_value_mapping["approval_status"] = approval_status.value

        id = self.db_client.add_new_data_source(
            column_value_mappings=source_column_value_mapping
        )
        return CreatedDataSource(id=id, name=cds.name)

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
        self, location_id: Optional[int] = None, **additional_column_value_mappings
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
        self, user_id: Optional[int] = None, **column_value_kwargs
    ) -> TestDataRequestInfo:
        if user_id is None:
            user_id = self.user().id

        submission_notes = self.test_name()
        data_request_id = self.db_client.create_data_request(
            column_value_mappings={
                "submission_notes": submission_notes,
                "title": get_test_name(),
                "creator_user_id": user_id,
                **column_value_kwargs,
            }
        )
        return TestDataRequestInfo(
            id=data_request_id, submission_notes=submission_notes
        )

    def user_follow_location(self, user_id: int, location_id: int):
        self.db_client.create_followed_search(
            column_value_mappings={"user_id": user_id, "location_id": location_id}
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
        self.tdc.db_client.update_data_source(
            entry_id=ds_info.id,
            column_edit_mappings={
                "approval_status_updated_at": self.notification_valid_date
            },
        )
        self.tdc.user_follow_location(user_id=user_id, location_id=locality_location_id)
        return ds_info.id

    def _create_data_request(self, request_status: RequestStatus, user_id: int) -> int:
        dr_info = self.tdc.data_request()
        locality_location_id = self.tdc.locality()
        self.tdc.db_client.update_data_request(
            column_edit_mappings={"request_status": request_status.value},
            entry_id=dr_info.id,
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
