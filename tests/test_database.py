"""
These functions test various database-internal views and functions.
This is distinct from the functions in the `database_client` module
which test the database-external views and functions
"""

import uuid
from collections import namedtuple
from datetime import datetime, timedelta, timezone

import pytest

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import ApprovalStatus, URLStatus
from database_client.models.core import RecentSearch
from middleware.enums import Relations, OperationType
from tests.conftest import live_database_client, test_data_creator_db_client
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.helper_classes.MultiLocationSetup import MultiLocationSetup
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import (
    TestDataCreatorDBClient,
)
from tests.helper_scripts.test_dataclasses import TestAgencyInfo
from utilities.enums import RecordCategories

ID_COLUMN = "state_iso"
FAKE_STATE_INFO = {"state_iso": "ZZ", "state_name": "Zaldoniza"}
FAKE_COUNTY_INFO = {
    "fips": "54321",
    "name": "Zipzapzibbidybop",
}
FAKE_LOCALITY_INFO = {"name": "Zoolazoolio"}

FakeLocationsInfo = namedtuple(
    "FakeLocationsInfo", ["state_id", "county_id", "locality_id"]
)


@pytest.fixture
def setup_fake_locations(live_database_client: DatabaseClient):
    # Populate `us_states` with data, returning id
    state_id = live_database_client.create_or_get(
        table_name=Relations.US_STATES.value,
        column_value_mappings=FAKE_STATE_INFO,
    )
    # Populate `counties` with data, returning id
    FAKE_COUNTY_INFO.update({"state_id": state_id})
    county_id = live_database_client.create_or_get(
        table_name=Relations.COUNTIES.value,
        column_value_mappings=FAKE_COUNTY_INFO,
    )
    # Populate `localities` with data, returning id
    FAKE_LOCALITY_INFO.update({"county_id": county_id})
    locality_id = live_database_client.create_or_get(
        table_name=Relations.LOCALITIES.value,
        column_value_mappings=FAKE_LOCALITY_INFO,
    )

    yield FakeLocationsInfo(state_id, county_id, locality_id)

    # After execution, delete rows in `us_states`, `counties`, and `localities`
    for relation, id_ in (
        (Relations.US_STATES, state_id),
        (Relations.COUNTIES, county_id),
        (Relations.LOCALITIES, locality_id),
    ):
        live_database_client._delete_from_table(
            table_name=relation.value,
            id_column_value=id_,
        )


def test_locations(
    live_database_client: DatabaseClient, setup_fake_locations: FakeLocationsInfo
):
    """
    Test the following:
        * that if a row in `us_states`, `counties`, or `localities` is created,
            the corresponding row(s) in the `locations` table are also created
        * that if a row in `us_states`, `counties`, or `localities` is deleted,
            the corresponding row(s) in the `locations` table are also deleted
    :param live_database_client:
    :return:
    """
    fake_locations_info = setup_fake_locations

    ID_COLUMN_ARRAY = ["id"]
    # First, validate that all rows are present initially in their respective tables
    results = live_database_client._select_from_relation(
        relation_name="us_states",
        columns=ID_COLUMN_ARRAY,
        where_mappings=WhereMapping.from_dict(FAKE_STATE_INFO),
    )
    assert fake_locations_info.state_id == results[0]["id"]

    results = live_database_client._select_from_relation(
        relation_name="counties",
        columns=ID_COLUMN_ARRAY,
        where_mappings=WhereMapping.from_dict(FAKE_COUNTY_INFO),
    )
    assert fake_locations_info.county_id == results[0]["id"]

    results = live_database_client._select_from_relation(
        relation_name="localities",
        columns=ID_COLUMN_ARRAY,
        where_mappings=WhereMapping.from_dict(FAKE_LOCALITY_INFO),
    )
    assert fake_locations_info.locality_id == results[0]["id"]

    # Assert locations are present in `locations`
    results = live_database_client._select_from_relation(
        relation_name="locations",
        columns=["state_id", "county_id", "locality_id"],
        where_mappings=WhereMapping.from_dict(
            {"state_id": fake_locations_info.state_id}
        ),
    )
    assert len(results) == 3

    def any_match(l: list[dict], d: dict):
        for r in l:
            if r == d:
                return True
        return False

    assert any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": fake_locations_info.county_id,
            "locality_id": fake_locations_info.locality_id,
        },
    )
    assert any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": fake_locations_info.county_id,
            "locality_id": None,
        },
    )
    assert any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": None,
            "locality_id": None,
        },
    )

    live_database_client._delete_from_table(
        table_name="localities",
        id_column_value=fake_locations_info.locality_id,
    )

    results = live_database_client._select_from_relation(
        relation_name="locations",
        columns=["state_id", "county_id", "locality_id"],
        where_mappings=WhereMapping.from_dict(
            {"state_id": fake_locations_info.state_id}
        ),
    )
    assert len(results) == 2
    assert not any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": fake_locations_info.county_id,
            "locality_id": fake_locations_info.locality_id,
        },
    )

    live_database_client._delete_from_table(
        table_name="counties",
        id_column_value=fake_locations_info.county_id,
    )

    results = live_database_client._select_from_relation(
        relation_name="locations",
        columns=["state_id", "county_id", "locality_id"],
        where_mappings=WhereMapping.from_dict(
            {"state_id": fake_locations_info.state_id}
        ),
    )
    assert len(results) == 1
    assert not any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": fake_locations_info.county_id,
            "locality_id": None,
        },
    )

    live_database_client._delete_from_table(
        table_name="us_states",
        id_column_value=fake_locations_info.state_id,
    )

    results = live_database_client._select_from_relation(
        relation_name="locations",
        columns=["state_id", "county_id", "locality_id"],
        where_mappings=WhereMapping.from_dict(
            {"state_id": fake_locations_info.state_id}
        ),
    )
    assert len(results) == 0


LinkUserFollowedTestInfo = namedtuple(
    "LinkUserFollowedTestInfo", ["user_id", "locality_id", "location_id"]
)


@pytest.fixture
def link_user_followed_test_info(
    live_database_client: DatabaseClient,
) -> LinkUserFollowedTestInfo:
    county_id = live_database_client._select_from_relation(
        relation_name=Relations.LOCATIONS_EXPANDED.value,
        columns=["county_id"],
        where_mappings=WhereMapping.from_dict(
            {
                "state_iso": "PA",
                "county_name": "Allegheny",
            }
        ),
    )[0]["county_id"]

    locality_id = live_database_client.create_locality(
        table_name=Relations.LOCALITIES.value,
        column_value_mappings={"county_id": county_id, "name": get_test_name()},
    )

    # Get newly created location id
    location_id = live_database_client.get_location_id(
        where_mappings=WhereMapping.from_dict(
            {
                "state_iso": "PA",
                "county_id": county_id,
                "locality_id": locality_id,
            }
        )
    )

    user_id = live_database_client.create_new_user(
        email=get_test_name(), password_digest=uuid.uuid4().hex
    )

    live_database_client.create_followed_search(
        column_value_mappings={
            "user_id": user_id,
            "location_id": location_id,
        }
    )

    yield LinkUserFollowedTestInfo(user_id, locality_id, location_id)

    for relation, id_ in (
        (Relations.LOCATIONS, location_id),
        (Relations.LOCALITIES, locality_id),
        (Relations.USERS, user_id),
    ):
        live_database_client._delete_from_table(
            table_name=relation.value, id_column_value=id_
        )


def test_link_user_followed_locations_link_exists(
    live_database_client: DatabaseClient, link_user_followed_test_info
):
    test_info = link_user_followed_test_info

    results = live_database_client._select_from_relation(
        relation_name=Relations.LINK_USER_FOLLOWED_LOCATION.value,
        columns=["user_id"],
        where_mappings=WhereMapping.from_dict({"location_id": test_info.location_id}),
    )
    assert len(results) == 1
    assert results[0]["user_id"] == test_info.user_id

    results = live_database_client._select_from_relation(
        relation_name=Relations.LINK_USER_FOLLOWED_LOCATION.value,
        columns=["location_id"],
        where_mappings=WhereMapping.from_dict({"user_id": test_info.user_id}),
    )
    assert len(results) == 1
    assert results[0]["location_id"] == test_info.location_id


def test_link_user_followed_locations_link_user_deletion_cascade(
    live_database_client: DatabaseClient, link_user_followed_test_info
):
    test_info = link_user_followed_test_info

    live_database_client._delete_from_table(
        table_name=Relations.USERS.value, id_column_value=test_info.user_id
    )

    assert_link_user_followed_location_deleted(live_database_client, test_info)


def test_link_user_followed_locations_link_location_deletion_cascade(
    live_database_client: DatabaseClient, link_user_followed_test_info
):
    test_info = link_user_followed_test_info

    live_database_client._delete_from_table(
        table_name=Relations.LOCALITIES.value, id_column_value=test_info.locality_id
    )

    assert_link_user_followed_location_deleted(live_database_client, test_info)


def assert_link_user_followed_location_deleted(live_database_client, test_info):
    results = live_database_client._select_from_relation(
        relation_name=Relations.LINK_USER_FOLLOWED_LOCATION.value,
        columns=["user_id"],
        where_mappings=WhereMapping.from_dict({"location_id": test_info.location_id}),
    )
    assert len(results) == 0
    results = live_database_client._select_from_relation(
        relation_name=Relations.LINK_USER_FOLLOWED_LOCATION.value,
        columns=["location_id"],
        where_mappings=WhereMapping.from_dict({"user_id": test_info.user_id}),
    )
    assert len(results) == 0


def test_data_sources_created_at_updated_at(
    test_data_creator_db_client: TestDataCreatorDBClient, live_database_client
):
    tdc = test_data_creator_db_client
    # Create bare-minimum fake data source
    data_source_id = tdc.data_source().id
    result = live_database_client._select_from_relation(
        relation_name=Relations.DATA_SOURCES.value,
        columns=["created_at", "updated_at"],
        where_mappings=WhereMapping.from_dict({"id": data_source_id}),
    )

    # Get `created_at` and `updated_at` for data source
    created_at = result[0]["created_at"]
    updated_at = result[0]["updated_at"]

    # Confirm they are equivalent
    assert created_at == updated_at

    # Update data source
    live_database_client.update_data_source(
        entry_id=data_source_id,
        column_edit_mappings={"name": get_test_name()},
    )

    # Get `updated_at` for data source
    result = live_database_client._select_from_relation(
        relation_name=Relations.DATA_SOURCES.value,
        columns=["updated_at"],
        where_mappings=WhereMapping.from_dict({"id": data_source_id}),
    )

    # Confirm `updated_at` is now greater than `created_at`
    assert result[0]["updated_at"] > created_at


def test_approval_status_updated_at(
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    tdc = test_data_creator_db_client
    # Create bare-minimum fake data source
    data_source_id = tdc.data_source(approval_status=ApprovalStatus.PENDING).id

    def get_approval_status_updated_at():
        return tdc.db_client._select_single_entry_from_relation(
            relation_name=Relations.DATA_SOURCES.value,
            columns=["approval_status_updated_at"],
            where_mappings=WhereMapping.from_dict({"id": data_source_id}),
        )["approval_status_updated_at"]

    def update_data_source(column_edit_mappings):
        tdc.db_client.update_data_source(
            entry_id=data_source_id,
            column_edit_mappings=column_edit_mappings,
        )

    initial_approval_status_updated_at = get_approval_status_updated_at()

    # Update approval status
    update_data_source({"approval_status": ApprovalStatus.APPROVED.value})
    # Get `approval_status_updated_at` for data request
    approval_status_updated_at = get_approval_status_updated_at()

    # Confirm `approval_status_updated_at` is now greater than `initial_approval_status_updated_at`
    assert approval_status_updated_at > initial_approval_status_updated_at

    # Make an edit to a different column and confirm that `approval_status_updated_at` is not updated
    update_data_source({"name": get_test_name()})

    new_approval_status_updated_at = get_approval_status_updated_at()
    assert approval_status_updated_at == new_approval_status_updated_at


def test_dependent_locations_view(test_data_creator_db_client: TestDataCreatorDBClient):
    tdc = test_data_creator_db_client
    mls = MultiLocationSetup(tdc)

    def is_dependent_location(dependent_location_id: int, parent_location_id: int):
        results = tdc.db_client._select_from_relation(
            relation_name=Relations.DEPENDENT_LOCATIONS.value,
            columns=["dependent_location_id"],
            where_mappings={
                "parent_location_id": parent_location_id,
                "dependent_location_id": dependent_location_id,
            },
        )
        return len(results) == 1

    # Confirm that in the dependent locations view, Pittsburgh is a
    # dependent location of both Allegheny County and Pennsylvania
    assert is_dependent_location(
        dependent_location_id=mls.pittsburgh_id,
        parent_location_id=mls.allegheny_county_id,
    )

    assert is_dependent_location(
        dependent_location_id=mls.pittsburgh_id, parent_location_id=mls.pennsylvania_id
    )

    # Confirm that in the dependent locations view, Allegheny County is
    # a dependent location of Pennsylvania
    assert is_dependent_location(
        dependent_location_id=mls.allegheny_county_id,
        parent_location_id=mls.pennsylvania_id,
    )

    # Confirm that in the dependent locations view, Allegheny County is NOT
    # a dependent location of California
    assert not is_dependent_location(
        dependent_location_id=mls.allegheny_county_id,
        parent_location_id=mls.california_id,
    )

    # And that the locality is NOT a dependent location of California
    assert not is_dependent_location(
        dependent_location_id=mls.pittsburgh_id, parent_location_id=mls.california_id
    )

    # Confirm that in the dependent locations view, the locality is NOT
    # a dependent location of Orange County
    assert not is_dependent_location(
        dependent_location_id=mls.pittsburgh_id, parent_location_id=mls.orange_county_id
    )


def test_link_recent_search_record_types_rows_deleted_on_recent_searches_delete(
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    tdc = test_data_creator_db_client

    user_info = tdc.user()
    location_id = tdc.locality()

    # Insert into recent searches and link_recent_search_record_types
    tdc.db_client.create_search_record(
        user_id=user_info.id,
        location_id=location_id,
        record_categories=[RecordCategories.AGENCIES, RecordCategories.JAIL],
    )

    # Delete recent searches
    recent_search = tdc.db_client._select_from_relation(
        relation_name=Relations.RECENT_SEARCHES.value,
        columns=["id"],
        where_mappings={"user_id": user_info.id, "location_id": location_id},
    )

    recent_search_id = recent_search[0]["id"]

    def get_link_table_rows():
        return tdc.db_client._select_from_relation(
            relation_name=Relations.LINK_RECENT_SEARCH_RECORD_CATEGORIES.value,
            columns=["id"],
            where_mappings={"recent_search_id": recent_search_id},
        )

    # Confirm that two rows exist in the link table
    link_table_rows = get_link_table_rows()
    assert len(link_table_rows) == 2

    tdc.db_client._delete_from_table(
        table_name=Relations.RECENT_SEARCHES.value,
        id_column_value=recent_search[0]["id"],
    )

    # Confirm that no row exists in the link table
    results = get_link_table_rows()
    assert len(results) == 0


def test_recent_searches_row_limit_maintained(
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    tdc = test_data_creator_db_client

    user_1 = tdc.user()
    user_2 = tdc.user()
    location_id = tdc.locality()

    # Add a search for each user
    def create_search_record(user_id: int):
        tdc.db_client.create_search_record(
            user_id=user_id,
            location_id=location_id,
            record_categories=[RecordCategories.ALL],
        )

    create_search_record(user_1.id)
    create_search_record(user_2.id)

    # Get the search record id for each user
    def get_search_record_id(user_id: int):
        results = tdc.db_client._select_from_relation(
            relation_name=Relations.RECENT_SEARCHES.value,
            columns=["id"],
            where_mappings={"user_id": user_id, "location_id": location_id},
        )
        return results[0]["id"]

    user_1_search_record_id = get_search_record_id(user_1.id)
    user_2_search_record_id = get_search_record_id(user_2.id)

    # For each user, add 49 additional rows
    def add_49_rows(user_id: int):
        session = tdc.db_client.session_maker()
        objects = []
        for i in range(49):
            objects.append(RecentSearch(user_id=user_id, location_id=location_id))
        session.bulk_save_objects(objects)
        session.commit()

    add_49_rows(user_1.id)
    add_49_rows(user_2.id)

    # Add one more search to user 1
    create_search_record(user_1.id)

    # Get recent searches for both users
    def get_recent_searches(user_id: int) -> list[int]:
        results = tdc.db_client._select_from_relation(
            relation_name=Relations.RECENT_SEARCHES.value,
            columns=["id"],
            where_mappings={"user_id": user_id, "location_id": location_id},
        )
        return [result["id"] for result in results]

    user_1_recent_searches = get_recent_searches(user_1.id)
    user_2_recent_searches = get_recent_searches(user_2.id)

    # Confirm that both users have 50 recent searches
    assert len(user_1_recent_searches) == 50
    assert len(user_2_recent_searches) == 50

    # Confirm that the original recent search id is no longer in the list for user 1
    assert user_1_search_record_id not in user_1_recent_searches

    # Confirm that the original recent search id remains in the list for user 2
    assert user_2_search_record_id in user_2_recent_searches


def test_update_broken_source_url_as_of(
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    tdc = test_data_creator_db_client

    now = datetime.now(timezone.utc)

    # Create data source
    cds = tdc.data_source(approval_status=ApprovalStatus.APPROVED)

    def get_broken_source_url_as_of():
        return tdc.db_client._select_single_entry_from_relation(
            relation_name=Relations.DATA_SOURCES.value,
            columns=["broken_source_url_as_of"],
            where_mappings=WhereMapping.from_dict({"id": cds.id}),
        )["broken_source_url_as_of"]

    # Get broken_source_url_as_of, confirm it is null
    assert get_broken_source_url_as_of() is None

    # Update source url to `broken`
    tdc.db_client._update_entry_in_table(
        table_name=Relations.DATA_SOURCES.value,
        entry_id=cds.id,
        column_edit_mappings={"url_status": URLStatus.BROKEN.value},
    )

    # Confirm broken_source_url_as_of is updated
    # (Allow a margin of error accounting for timezone chicanery)
    now_pre = now - timedelta(hours=1)
    now_post = now + timedelta(hours=1)
    assert now_pre < get_broken_source_url_as_of() < now_post


# The below tests pass locally but not in CI
# def test_agencies_unique_constraint(
#     test_data_creator_db_client: TestDataCreatorDBClient,
# ):
#     tdc = test_data_creator_db_client
#
#     # Create two agencies with the same name
#     location_id = tdc.locality()
#     db_client = tdc.db_client
#     db_client.create_agency(
#         column_value_mappings={
#             "name": "Test Agency",
#             "location_id": location_id,
#             "jurisdiction_type": JurisdictionType.LOCAL.value,
#         }
#     )
#     with pytest.raises(IntegrityError):
#         db_client.create_agency(
#             column_value_mappings={
#                 "name": "Test Agency",
#                 "location_id": location_id,
#                 "jurisdiction_type": JurisdictionType.LOCAL.value,
#             }
#         )
#     # Other combinations should not raise integrity error
#     db_client.create_agency(
#         column_value_mappings={
#             "name": "Test Agency",
#             "location_id": location_id,
#             "jurisdiction_type": JurisdictionType.STATE.value,
#         }
#     )
#     db_client.create_agency(
#         column_value_mappings={
#             "name": "Test Agency",
#             "location_id": tdc.locality(),
#             "jurisdiction_type": JurisdictionType.LOCAL.value,
#         }
#     )
#
#
# def test_data_sources_unique_constraint(
#     test_data_creator_db_client: TestDataCreatorDBClient,
# ):
#     tdc = test_data_creator_db_client
#
#     # Create two data sources with the same name
#     db_client = tdc.db_client
#     db_client.add_new_data_source(
#         column_value_mappings={
#             "name": "Test Data Source",
#             "source_url": "http://test.com",
#             "record_type_id": 1,
#         }
#     )
#     with pytest.raises(IntegrityError):
#         db_client.add_new_data_source(
#             column_value_mappings={
#                 "name": "Test Data Source",
#                 "source_url": "http://test.com",
#                 "record_type_id": 1,
#             }
#         )
#     # Other combinations should not raise integrity error
#     db_client.add_new_data_source(
#         column_value_mappings={
#             "name": "Test Data Source",
#             "source_url": "http://test.com",
#             "record_type_id": 2,
#         }
#     )
#     db_client.add_new_data_source(
#         column_value_mappings={
#             "name": "Test Data Source",
#             "source_url": "http://other-test.com",
#             "record_type_id": 1,
#         }
#     )


def delete_change_log(db_client):
    db_client.execute_raw_sql("DELETE FROM CHANGE_LOG;")


def test_localities_table_log_logic(
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    tdc = test_data_creator_db_client
    db_client = tdc.db_client
    delete_change_log(db_client)

    old_name = get_test_name()
    new_name = get_test_name()

    # Create locality
    location_id = tdc.locality(locality_name=old_name)
    locality_id = db_client.get_locality_id_by_location_id(location_id)
    # Check that creation is logged:
    logs = db_client.get_change_logs_for_table(Relations.LOCALITIES)
    assert len(logs) == 1

    # Change locality name
    db_client._update_entry_in_table(
        table_name=Relations.LOCALITIES.value,
        entry_id=locality_id,
        column_edit_mappings={"name": new_name},
    )
    # Check that update is logged for `localities`
    logs = db_client.get_change_logs_for_table(Relations.LOCALITIES)
    assert len(logs) == 2
    log = logs[1]
    assert log["operation_type"] == OperationType.UPDATE.value
    assert log["table_name"] == Relations.LOCALITIES.value
    assert log["affected_id"] == locality_id
    assert log["old_data"] == {"name": old_name}
    assert log["new_data"] == {"name": new_name}
    assert log["created_at"] is not None
    # Delete locality
    db_client._delete_from_table(
        table_name=Relations.LOCALITIES.value, id_column_value=locality_id
    )
    # Check that delete is logged for `localities`
    logs = db_client.get_change_logs_for_table(Relations.LOCALITIES)
    assert len(logs) == 3
    log = logs[2]
    assert log["operation_type"] == OperationType.DELETE.value
    assert log["affected_id"] == locality_id
    assert log["old_data"] == {"id": locality_id, "county_id": 1, "name": new_name}
    assert log["new_data"] is None


def test_counties_table_log_logic(test_data_creator_db_client: TestDataCreatorDBClient):

    tdc = test_data_creator_db_client
    delete_change_log(tdc.db_client)

    new_name = get_test_name()
    old_name = get_test_name()

    county_id = tdc.county(county_name=old_name)

    tdc.db_client._update_entry_in_table(
        table_name=Relations.COUNTIES.value,
        entry_id=county_id,
        column_edit_mappings={"name": new_name},
    )
    logs = tdc.db_client.get_change_logs_for_table(Relations.COUNTIES)
    assert len(logs) == 2
    log = logs[1]
    assert log["operation_type"] == OperationType.UPDATE.value
    assert log["table_name"] == Relations.COUNTIES.value
    assert log["affected_id"] == county_id
    assert log["old_data"] == {"name": old_name}
    assert log["new_data"] == {"name": new_name}
    assert log["created_at"] is not None

    tdc.db_client._delete_from_table(
        table_name=Relations.COUNTIES.value, id_column_value=county_id
    )
    logs = tdc.db_client.get_change_logs_for_table(Relations.COUNTIES)
    assert len(logs) == 3
    log = logs[2]
    assert log["operation_type"] == OperationType.DELETE.value
    assert log["affected_id"] == county_id
    assert len(list(log["old_data"].keys())) == 10
    assert log["new_data"] is None


def test_locations_table_log_logic(
    test_data_creator_db_client: TestDataCreatorDBClient,
):

    tdc = test_data_creator_db_client
    db_client = tdc.db_client
    delete_change_log(db_client)

    # Create locality
    locality_name = get_test_name()
    location_id = tdc.locality(locality_name)

    # Create county
    county_name = get_test_name()
    county_id = tdc.county(county_name)

    # Change locality's county to that county
    db_client._update_entry_in_table(
        table_name=Relations.LOCATIONS.value,
        entry_id=location_id,
        column_edit_mappings={"county_id": county_id},
    )
    # Check that update is logged for `locations`
    logs = db_client.get_change_logs_for_table(Relations.LOCATIONS)
    assert len(logs) == 3
    log = logs[2]
    assert log["operation_type"] == OperationType.UPDATE.value
    assert log["table_name"] == Relations.LOCATIONS.value
    assert log["affected_id"] == location_id
    assert log["old_data"] == {"county_id": 1}
    assert log["new_data"] == {"county_id": county_id}
    assert log["created_at"] is not None
    # Delete locality
    locality_id = db_client.get_locality_id_by_location_id(location_id)
    db_client._delete_from_table(
        table_name=Relations.LOCALITIES.value, id_column_value=locality_id
    )
    # Check that delete is logged for `locations`
    logs = db_client.get_change_logs_for_table(Relations.LOCATIONS)
    assert len(logs) == 4
    log = logs[3]
    assert log["operation_type"] == OperationType.DELETE.value
    assert log["affected_id"] == location_id
    assert log["old_data"] == {
        "id": location_id,
        "state_id": 1,
        "county_id": county_id,
        "locality_id": locality_id,
        "lat": None,
        "lng": None,
        "type": "Locality",
    }
    assert log["new_data"] is None


def test_agencies_table_logic(test_data_creator_db_client: TestDataCreatorDBClient):
    tdc = test_data_creator_db_client
    db_client = tdc.db_client
    delete_change_log(db_client)

    NUMBER_OF_AGENCY_TABLE_COLUMNS = 18

    # Create agency
    old_name = get_test_name()
    new_name = get_test_name()
    agency_info: TestAgencyInfo = tdc.agency(name=old_name)

    # Update agency name
    db_client._update_entry_in_table(
        table_name=Relations.AGENCIES.value,
        entry_id=agency_info.id,
        column_edit_mappings={"name": new_name},
    )
    # Check that update is logged for `agencies`
    logs = db_client.get_change_logs_for_table(Relations.AGENCIES)
    assert len(logs) == 2
    log = logs[1]
    assert log["operation_type"] == OperationType.UPDATE.value
    assert log["table_name"] == Relations.AGENCIES.value
    assert log["affected_id"] == agency_info.id
    assert log["old_data"] == {"name": old_name}
    assert log["new_data"] == {"name": new_name}
    assert log["created_at"] is not None

    # Delete agency
    db_client._delete_from_table(
        table_name=Relations.AGENCIES.value, id_column_value=agency_info.id
    )
    # Check that delete is logged for `agencies`
    logs = db_client.get_change_logs_for_table(Relations.AGENCIES)
    assert len(logs) == 3
    log = logs[2]
    assert log["operation_type"] == OperationType.DELETE.value
    assert log["affected_id"] == agency_info.id
    assert len(log["old_data"].keys()) == NUMBER_OF_AGENCY_TABLE_COLUMNS
    assert log["new_data"] is None
