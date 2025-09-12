"""
Module for testing database client functionality against a live database
"""

import uuid

import pytest
import sqlalchemy
from sqlalchemy import select

from db.client.core import DatabaseClient
from db.db_client_dataclasses import (
    OrderByParameters,
)
from db.subquery_logic import SubqueryParameterManager
from db.enums import (
    SortOrder,
    RequestStatus,
)
from db.models.table_reference import SQL_ALCHEMY_TABLE_REFERENCE
from middleware.enums import Relations
from tests.helpers.common_test_data import (
    get_random_number_for_testing,
    get_test_name,
)
from tests.helpers.complex_test_data_creation_functions import (
    create_data_source_entry_for_url_duplicate_checking,
)

from tests.helpers.helper_classes.AnyOrder import AnyOrder
from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.helpers.test_dataclasses import TestDataRequestInfo
from tests.helpers.helper_functions_complex import (
    create_test_user_db_client,
)
from utilities.enums import RecordCategoryEnum


def test_get_data_requests_for_creator(live_database_client: DatabaseClient):
    test_user = create_test_user_db_client(live_database_client)
    submission_notes_list = [uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex]

    for submission_notes in submission_notes_list:
        live_database_client.create_data_request(
            column_value_mappings={
                "submission_notes": submission_notes,
                "title": get_test_name(),
                "creator_user_id": test_user.user_id,
            }
        )

    results = live_database_client.get_data_requests_for_creator(
        test_user.user_id, columns=["submission_notes"]
    )
    assert len(results) == 3
    for result in results:
        assert result["submission_notes"] in submission_notes_list


def test_user_is_creator_of_data_request(live_database_client):
    test_user = create_test_user_db_client(live_database_client)
    submission_notes = uuid.uuid4().hex

    # Test with entry where user is listed as creator
    data_request_id = live_database_client.create_data_request(
        column_value_mappings={
            "submission_notes": submission_notes,
            "title": get_test_name(),
            "creator_user_id": test_user.user_id,
        }
    )

    results = live_database_client.user_is_creator_of_data_request(
        user_id=test_user.user_id, data_request_id=data_request_id
    )
    assert results is True

    # Test with entry where user is not listed as creator
    data_request_id = live_database_client.create_data_request(
        column_value_mappings={
            "submission_notes": submission_notes,
            "title": get_test_name(),
        }
    )

    results = live_database_client.user_is_creator_of_data_request(
        user_id=test_user.user_id, data_request_id=data_request_id
    )
    assert results is False


# Commented out until: https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/458
# def test_get_agencies_without_homepage_urls(live_database_client):
#     submitted_name = create_agency_entry_for_search_cache(
#         db_client=live_database_client
#     )
#
#     results = live_database_client.get_agencies_without_homepage_urls()
#     assert len(results) > 1
#     assert results[0]["submitted_name"] == submitted_name
#     assert list(results[0].keys()) == [
#         "submitted_name",
#         "jurisdiction_type",
#         "state_iso",
#         "municipality",
#         "county_name",
#         "airtable_uid",
#         "count_data_sources",
#         "zip_code",
#         "no_web_presence",
#     ]

# Commented out until: https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/458
# def test_create_search_cache_entry(live_database_client):
#     submitted_name = create_agency_entry_for_search_cache(
#         db_client=live_database_client
#     )
#
#     result_to_update = live_database_client.get_agencies_without_homepage_urls()[0]
#
#     airtable_uid = result_to_update["airtable_uid"]
#
#     fake_search_result = "found_results"
#     live_database_client.create_search_cache_entry(
#         column_value_mappings={
#             "agency_airtable_uid": airtable_uid,
#             "search_result": fake_search_result,
#         }
#     )
#
#     # Check the first result is now different
#     new_result = live_database_client.get_agencies_without_homepage_urls()[0]
#     assert new_result["airtable_uid"] != airtable_uid


def test_create_request_source_relation(
    test_data_creator_db_client: TestDataCreatorDBClient, live_database_client
):
    tdc = test_data_creator_db_client
    # Create data source and request
    source_info = tdc.data_source()
    source_id = source_info.id
    request_info = tdc.data_request()
    request_id = request_info.id

    # Try to add twice and get a unique violation
    live_database_client.create_request_source_relation(
        column_value_mappings={"request_id": request_id, "data_source_id": source_id}
    )
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        live_database_client.create_request_source_relation(
            column_value_mappings={
                "request_id": request_id,
                "data_source_id": source_id,
            }
        )


def test_check_for_url_duplicates(live_database_client):
    create_data_source_entry_for_url_duplicate_checking(live_database_client)

    # Happy path
    non_duplicate_url = "not-a-duplicate.com"
    results = live_database_client.check_for_url_duplicates(non_duplicate_url)
    assert len(results) == 0

    duplicate_base_url = "duplicate-checker.com"
    results = live_database_client.check_for_url_duplicates(duplicate_base_url)
    assert len(results) == 1


def test_get_columns_for_relation(live_database_client):
    columns = live_database_client.get_columns_for_relation(Relations.TEST_TABLE)

    assert columns == ["id", "pet_name", "species"]


def test_create_or_get(live_database_client):
    results = live_database_client.create_or_get(
        table_name="test_table",
        column_value_mappings={"pet_name": "Schnoodles", "species": "Rat"},
    )

    assert results

    # Check that the same results are returned if the entry already exists
    new_results = live_database_client.create_or_get(
        table_name="test_table",
        column_value_mappings={"pet_name": "Schnoodles", "species": "Rat"},
    )

    assert results == new_results


def test_get_data_requests(test_data_creator_db_client: TestDataCreatorDBClient):
    tdc = test_data_creator_db_client

    # Create a data request to ensure there's at least one data request in the database
    tdc.data_request()

    results = tdc.db_client.get_data_requests(
        columns=["id"], subquery_parameters=[SubqueryParameterManager.data_sources()]
    )
    assert results


def test_get_linked_rows(
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    tdc = test_data_creator_db_client

    # Create a data request to ensure there's at least one data request in the database
    dr_id = tdc.data_request().id
    ds_info = tdc.data_source()
    tdc.link_data_request_to_data_source(
        data_request_id=dr_id,
        data_source_id=ds_info.id,
    )
    #
    results = tdc.db_client.get_linked_rows(
        link_table=Relations.LINK_DATA_SOURCES_DATA_REQUESTS,
        left_id=dr_id,
        left_link_column="request_id",
        right_link_column="data_source_id",
        linked_relation=Relations.DATA_SOURCES,
        linked_relation_linking_column="id",
        columns_to_retrieve=[
            "id",
            "name",
        ],
        build_metadata=True,
    )

    assert results["metadata"]["count"] == len(results["data"]) > 0
    assert results["data"][0]["name"] == ds_info.name
    assert results["data"][0]["id"] == ds_info.id


def test_get_unarchived_data_requests_with_issues(
    test_data_creator_db_client: TestDataCreatorDBClient, clear_data_requests
):
    # Add data requests with issues
    tdc = test_data_creator_db_client

    def create_data_request_with_issue_and_request_status(
        request_status: RequestStatus,
    ) -> TestDataRequestInfo:
        dr_info = tdc.data_request(request_status=request_status)
        issue_number = get_random_number_for_testing()
        tdc.db_client.create_data_request_github_info(
            column_value_mappings={
                "data_request_id": dr_info.id,
                "github_issue_url": f"https://github.com/test-org/test-repo/issues/{issue_number}",
                "github_issue_number": issue_number,
            }
        )

        return dr_info

    dr_info_active = create_data_request_with_issue_and_request_status(
        RequestStatus.ACTIVE
    )
    create_data_request_with_issue_and_request_status(RequestStatus.ARCHIVED)

    results = tdc.db_client.get_unarchived_data_requests_with_issues()

    assert len(results) == 1
    result = results[0]

    assert result.data_request_id == dr_info_active.id
    # Check result contains all requisite columns
    assert result.github_issue_url
    assert result.github_issue_number
    assert result.request_status == RequestStatus.ACTIVE


def test_user_followed_searches_logic(
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    tdc = test_data_creator_db_client

    # Create a standard user
    user_info = tdc.user()

    # Have that user follow two searches
    tdc.db_client.create_followed_search(
        user_id=user_info.id,
        location_id=1,
    )

    tdc.db_client.create_followed_search(
        user_id=user_info.id,
        location_id=2,
    )

    # Get the user's followed searches
    results = tdc.db_client.get_user_followed_searches(user_id=user_info.id)
    assert len(results["data"]) == 2

    # Unfollow one of the searches
    tdc.db_client.delete_followed_search(
        user_id=user_info.id,
        location_id=1,
    )

    # Get the user's followed searches, and ensure the un-followed search is gone
    results = tdc.db_client.get_user_followed_searches(user_id=user_info.id)
    assert len(results["data"]) == 1


def test_get_next_user_events_and_mark_user_events_as_sent(test_data_creator_db_client):
    tdc = test_data_creator_db_client
    tdc.clear_test_data()

    # Create a notification event for an (implicitly created) user
    entity_id = tdc.create_valid_notification_event()

    # Create another user with two notification events
    user_id = tdc.user().id
    entity_id_2 = tdc.create_valid_notification_event(user_id=user_id)
    entity_id_3 = tdc.create_valid_notification_event(user_id=user_id)

    tdc.db_client.optionally_update_user_notification_queue()

    # Retrieve the single-event user and mark as sent,
    event_batch = tdc.db_client.get_next_user_event_batch()
    assert len(event_batch.events) == 1
    assert event_batch.events[0].entity_id == entity_id
    tdc.db_client.mark_user_events_as_sent(event_batch.user_id)

    # Run for the two-event user
    event_batch = tdc.db_client.get_next_user_event_batch()
    assert len(event_batch.events) == 2
    assert AnyOrder([event.entity_id for event in event_batch.events]) == [
        entity_id_2,
        entity_id_3,
    ] or AnyOrder([event.entity_id for event in event_batch.events]) == [
        entity_id_2,
        entity_id_3,
    ]

    tdc.db_client.mark_user_events_as_sent(event_batch.user_id)

    event_batch = tdc.db_client.get_next_user_event_batch()
    assert event_batch is None


def test_insert_search_record(test_data_creator_db_client: TestDataCreatorDBClient):
    tdc = test_data_creator_db_client
    user_info = tdc.user()
    location_id = tdc.locality()

    def assert_are_expected_record_categories(
        rc_ids: list[int], record_categories: list[RecordCategoryEnum]
    ):
        table = SQL_ALCHEMY_TABLE_REFERENCE[Relations.RECORD_CATEGORIES.value]
        name_column = getattr(table, "name")
        id_column = getattr(table, "id")
        query = select(name_column).where(id_column.in_(rc_ids))
        result = tdc.db_client.execute_sqlalchemy(lambda: query)
        result = [row[0] for row in result]
        result.sort()
        rc_values = [rc.value for rc in record_categories]
        rc_values.sort()
        assert result == rc_values

    def get_recent_searches():
        return tdc.db_client._select_from_relation(
            relation_name=Relations.RECENT_SEARCHES.value,
            columns=["id"],
            where_mappings={"user_id": user_info.id, "location_id": location_id},
            order_by=OrderByParameters(
                sort_by="created_at", sort_order=SortOrder.ASCENDING
            ),
        )

    def get_link_recent_search_record_types(recent_search_id: int):
        return tdc.db_client._select_from_relation(
            relation_name=Relations.LINK_RECENT_SEARCH_RECORD_CATEGORIES.value,
            columns=["record_category_id"],
            where_mappings={"recent_search_id": recent_search_id},
        )

    tdc.db_client.create_search_record(
        user_id=user_info.id,
        location_id=location_id,
        record_categories=RecordCategoryEnum.ALL,
    )

    # Confirm record exists in both `recent_searches` and `link_recent_search_record_types` tables
    recent_search_results = get_recent_searches()
    assert len(recent_search_results) == 1

    link_results = get_link_recent_search_record_types(recent_search_results[0]["id"])

    assert len(link_results) == 1

    # Confirm record category is all
    assert_are_expected_record_categories(
        rc_ids=[link_results[0]["record_category_id"]],
        record_categories=[RecordCategoryEnum.ALL],
    )

    tdc.db_client.create_search_record(
        user_id=user_info.id,
        location_id=location_id,
        record_categories=[RecordCategoryEnum.AGENCIES, RecordCategoryEnum.JAIL],
    )

    # Confirm two records now exists in `recent_searches` table associated with this information
    recent_search_results = get_recent_searches()
    assert len(recent_search_results) == 2

    # And that the second links to an `AGENCIES` and `JAIL` entry in `link_recent_search_record_types` table
    search_id = recent_search_results[1]["id"]
    link_results = get_link_recent_search_record_types(search_id)
    rc_ids = [link_result["record_category_id"] for link_result in link_results]

    assert_are_expected_record_categories(
        rc_ids=rc_ids,
        record_categories=[RecordCategoryEnum.AGENCIES, RecordCategoryEnum.JAIL],
    )


# TODO: This code currently doesn't work properly because it will repeatedly insert the same test data, throwing off counts
# def test_search_with_location_and_record_types_test_data(live_database_client, xylonslyvania_test_data):
#     results = live_database_client.search_with_location_and_record_type(
#         state="Xylonsylvania"
#     )
#     assert len(results) == 8
#
#     results = live_database_client.search_with_location_and_record_type(
#         state="Xylonsylvania",
#         record_type=RecordCategories.JAIL
#     )
#     assert len(results) == 6
#
#     results = live_database_client.search_with_location_and_record_type(
#         state="Xylonsylvania",
#         county="Arxylodon"
#     )
#     assert len(results) == 4
#
#     results = live_database_client.search_with_location_and_record_type(
#         state="Xylonsylvania",
#         county="Qtzylan",
#         locality="Qtzylschlitzl"
#     )
#     assert len(results) == 2
#
#     results = live_database_client.search_with_location_and_record_type(
#         state="Xylonsylvania",
#         record_type=RecordCategories.POLICE,
#         county="Arxylodon",
#         locality="Xylodammerung"
#     )
#
#     assert len(results) == 1
#     assert results[0].data_source_name == 'Xylodammerung Police Department Stops'
