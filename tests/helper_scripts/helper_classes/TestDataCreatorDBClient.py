import uuid
from typing import Optional

from sqlalchemy import delete, select

from database_client.database_client import DatabaseClient
from database_client.enums import ApprovalStatus
from database_client.models import SQL_ALCHEMY_TABLE_REFERENCE
from middleware.enums import JurisdictionType, Relations
from tests.helper_scripts.common_endpoint_calls import CreatedDataSource
from tests.helper_scripts.test_dataclasses import TestUserDBInfo, TestAgencyInfo, TestDataRequestInfo


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

    def delete_test_like(
        self,
        table_name: str,
        like_column_name: str,
    ):
        self.delete_like(
            table_name=table_name,
            like_column_name=like_column_name,
            like_text="TEST_%"
        )

    def get_county_id(self, county_name: str) -> int:
        # Note: This assumes a county name is unique
        # This isn't always true, but should suffice for testing
        table = SQL_ALCHEMY_TABLE_REFERENCE[Relations.COUNTIES.value]
        column_name = getattr(table, "name")
        column_id = getattr(table, "id")
        where_clause = column_name == county_name
        query = select(column_id).where(column_name == county_name)
        result = self.db_client.execute_sqlalchemy(lambda: query)
        return [row[0] for row in result][0]


class TestDataCreatorDBClient:
    """
    Creates test data for DatabaseClient tests, using a DatabaseClient
    """

    def __init__(self):
        self.db_client = DatabaseClient()
        self.helper = TDCSQLAlchemyHelper()

    def test_name(self):
        return f"TEST_{uuid.uuid4().hex}"

    def clear_test_data(self):
        # Remove test data from data request
        self.helper.delete_test_like(
            table_name=Relations.DATA_REQUESTS.value,
            like_column_name="submission_notes",
        )
        # Remove test data from user
        self.helper.delete_test_like(
            table_name=Relations.USERS.value,
            like_column_name="email",
        )

        # Remove test data from data source
        self.helper.delete_test_like(
            table_name=Relations.DATA_SOURCES.value,
            like_column_name="name",
        )

        # Remove test data from agency
        self.helper.delete_test_like(
            table_name=Relations.AGENCIES.value,
            like_column_name="submitted_name",
        )

        # Remove test data from locality
        self.helper.delete_test_like(
            table_name=Relations.LOCALITIES.value,
            like_column_name="name",
        )

    def locality(self) -> int:
        # Create locality and return location id
        county_id = self.helper.get_county_id(county_name="Allegheny")
        locality_name = self.test_name()
        locality_id = self.db_client.create_locality(
            column_value_mappings={
                "name": locality_name,
                "county_id": county_id
            }
        )
        location_id = self.db_client.get_location_id(
            where_mappings={
                "locality_id": locality_id
            }
        )
        return location_id



    def user(self) -> TestUserDBInfo:
        email = self.test_name()
        pw_digest = uuid.uuid4().hex

        user_id = self.db_client.create_new_user(email=email, password_digest=pw_digest)
        return TestUserDBInfo(id=user_id, email=email, password_digest=pw_digest)

    def data_source(self, approval_status: Optional[ApprovalStatus]) -> CreatedDataSource:
        cds = CreatedDataSource(id=uuid.uuid4().hex, name=uuid.uuid4().hex)
        source_column_value_mapping = {
            "name": cds.name,
        }
        if approval_status is not None:
            source_column_value_mapping["approval_status"] = approval_status.value

        id = self.db_client.add_new_data_source(
            column_value_mappings=source_column_value_mapping
        )
        return CreatedDataSource(
            id=id, name=cds.name
        )

    def link_data_request_to_location(
        self,
        data_request_id: int,
        location_id: int
    ):
        self.db_client.create_request_location_relation(
            column_value_mappings={
                "data_request_id": data_request_id,
                "location_id": location_id
            }
        )

    def link_data_source_to_agency(self, data_source_id: int, agency_id: int):
        self.db_client.create_data_source_agency_relation(
            column_value_mappings={
                "data_source_id": data_source_id,
                "agency_id": agency_id
            }
        )

    def update_data_source(self, data_source_id: int, column_value_mappings: dict):
        self.db_client.update_data_source(
            entry_id=data_source_id,
            column_edit_mappings=column_value_mappings
        )

    def agency(self, location_id: Optional[int] = None) -> TestAgencyInfo:
        agency_name = self.test_name()
        column_value_mappings = {
            "submitted_name": agency_name,
            "jurisdiction_type": JurisdictionType.FEDERAL.value
        }

        if location_id is not None:
            column_value_mappings["location_id"] = location_id

        agency_id = self.db_client.create_agency(
            column_value_mappings=column_value_mappings
        )
        return TestAgencyInfo(id=agency_id, submitted_name=agency_name)

    def update_agency(self, agency_id: int, column_value_mappings: dict):
        self.db_client.update_agency(
            entry_id=agency_id,
            column_value_mappings=column_value_mappings
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
                "title": uuid.uuid4().hex,
                "creator_user_id": user_id,
                **column_value_kwargs,
            }
        )
        return TestDataRequestInfo(
            id=data_request_id, submission_notes=submission_notes
        )

    def user_follow_location(
        self,
        user_id: int,
        location_id: int
    ):
        self.db_client.create_followed_search(
            column_value_mappings={
                "user_id": user_id,
                "location_id": location_id
            }
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
