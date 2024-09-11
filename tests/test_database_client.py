"""
Module for testing database client functionality against a live database
"""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy import insert, select, update

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import OrderByParameters, WhereMapping
from database_client.enums import (
    ExternalAccountTypeEnum,
    RelationRoleEnum,
    ColumnPermissionEnum,
    SortOrder,
)
from database_client.result_formatter import ResultFormatter
from middleware.exceptions import (
    UserNotFoundError,
)
from middleware.models import ExternalAccount, TestTable, User
from middleware.enums import PermissionsEnum
from tests.fixtures import (
    live_database_client,
    test_table_data,
)
from tests.helper_scripts.common_test_data import (
    insert_test_column_permission_data,
    create_agency_entry_for_search_cache,
)
from tests.helper_scripts.helper_functions import (
    insert_test_agencies_and_sources_if_not_exist,
    setup_get_typeahead_suggestion_test_data,
    create_test_user_db_client,
)
from utilities.enums import RecordCategories


def test_add_new_user(live_database_client: DatabaseClient):
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    result = (
        live_database_client.execute_sqlalchemy(
            lambda: select(User.password_digest, User.api_key).where(
                User.email == fake_email
            )
        )
        .mappings()
        .one_or_none()
    )

    password_digest = result.password_digest
    api_key = result.api_key

    assert api_key is not None
    assert password_digest == "test_password"


def test_get_user_id(live_database_client: DatabaseClient):
    # Add a new user to the database
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")

    # Directly fetch the user ID from the database for comparison
    direct_user_id = live_database_client.execute_sqlalchemy(
        lambda: select(User.id).where(User.email == fake_email)
    ).one_or_none()[0]

    # Get the user ID from the live database
    result_user_id = live_database_client.get_user_id(fake_email)

    # Compare the two user IDs
    assert result_user_id == direct_user_id


def test_link_external_account(live_database_client: DatabaseClient):
    fake_email = uuid.uuid4().hex
    fake_external_account_id = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    user_id = live_database_client.get_user_id(fake_email)
    live_database_client.link_external_account(
        user_id=str(user_id),
        external_account_id=fake_external_account_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )
    row = (
        live_database_client.execute_sqlalchemy(
            lambda: select(ExternalAccount.user_id, ExternalAccount.account_type).where(
                ExternalAccount.account_identifier == fake_external_account_id
            )
        )
        .mappings()
        .one_or_none()
    )

    assert row.user_id == user_id
    assert row.account_type == ExternalAccountTypeEnum.GITHUB.value


def test_get_user_info_by_external_account_id(live_database_client: DatabaseClient):
    fake_email = uuid.uuid4().hex
    fake_external_account_id = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    user_id = live_database_client.get_user_id(fake_email)
    live_database_client.link_external_account(
        user_id=str(user_id),
        external_account_id=fake_external_account_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )
    user_info = live_database_client.get_user_info_by_external_account_id(
        fake_external_account_id, ExternalAccountTypeEnum.GITHUB
    )
    assert user_info.email == fake_email


def test_set_user_password_digest(live_database_client: DatabaseClient):
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    live_database_client.set_user_password_digest(fake_email, "test_password")
    password_digest = live_database_client.execute_sqlalchemy(
        lambda: select(User.password_digest).where(User.email == fake_email)
    ).one_or_none()[0]

    assert password_digest == "test_password"


def test_reset_token_logic(live_database_client: DatabaseClient):
    fake_email = uuid.uuid4().hex
    fake_token = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    live_database_client.add_reset_token(fake_email, fake_token)
    reset_token_info = live_database_client.get_reset_token_info(fake_token)
    assert reset_token_info, "Token not found"
    assert reset_token_info.email == fake_email, "Email does not match"

    live_database_client.delete_reset_token(fake_email, fake_token)
    reset_token_info = live_database_client.get_reset_token_info(fake_token)
    assert reset_token_info is None, "Token not deleted"


def test_update_user_api_key(live_database_client: DatabaseClient):
    # Add a new user to the database
    email = uuid.uuid4().hex
    password_digest = uuid.uuid4().hex

    live_database_client.add_new_user(
        email=email,
        password_digest=password_digest,
    )

    original_user_info = live_database_client.get_user_info(email)

    # Update the user's API key with the DatabaseClient Method
    live_database_client.update_user_api_key(
        api_key="test_api_key", user_id=original_user_info.id
    )

    # Fetch the user's API key from the database to confirm the change
    user_info = live_database_client.get_user_info(email)
    assert original_user_info.api_key != user_info.api_key
    assert user_info.api_key == "test_api_key"


def test_select_from_single_relation_columns_only(
    test_table_data, live_database_client: DatabaseClient
):
    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
    )

    assert results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Jimbo"},
        {"pet_name": "Simon"},
    ]


def test_select_from_single_relation_where_mapping(live_database_client: DatabaseClient):
    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Aardvark")],
    )

    assert results == [
        {"pet_name": "Arthur"},
    ]

    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", eq=False, value="Aardvark")],
    )

    assert results == [
        {"pet_name": "Jimbo"},
        {"pet_name": "Simon"},
    ]


def test_select_from_single_relation_limit(live_database_client: DatabaseClient):
    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        limit=1,
    )

    assert results == [
        {"pet_name": "Arthur"},
    ]


def test_select_from_single_relation_limit_and_offset(live_database_client: DatabaseClient, monkeypatch):
    # Used alongside limit; we mock PAGE_SIZE to be one
    monkeypatch.setattr("database_client.database_client.PAGE_SIZE", 1)

    live_database_client.get_offset = MagicMock(return_value=1)

    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        limit=1,
        page=1,  # 1 is the second page; 0-indexed
    )

    assert results == [
        {"pet_name": "Jimbo"},
    ]


def test_select_from_single_relation_order_by(live_database_client: DatabaseClient):
    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        order_by=OrderByParameters(
            sort_by="species", sort_order=SortOrder.ASCENDING
        ),
    )

    assert results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Simon"},
        {"pet_name": "Jimbo"},
    ]


def test_select_from_single_relation_all_parameters(live_database_client: DatabaseClient, monkeypatch):
    # Used alongside limit; we mock PAGE_SIZE to be one
    monkeypatch.setattr("database_client.database_client.PAGE_SIZE", 1)

    # Add additional row to the table to test the offset and limit
    live_database_client.execute_sqlalchemy(
        lambda: insert(TestTable).values(pet_name="Ezekiel", species="Cat")
    )

    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        where_mappings=[
            WhereMapping(column="species", value="Aardvark"),
            WhereMapping(column="species", eq=False, value="Bear"),
        ],
        limit=1,
        page=1,  # 1 is the second page; 0-indexed
        order_by=OrderByParameters(
            sort_by="pet_name",
            sort_order=SortOrder.DESCENDING,
        ),
    )

    assert results == [
        {"pet_name": "Arthur"},
    ]


def test_create_entry_in_table_return_columns(live_database_client, test_table_data):
    id = live_database_client._create_entry_in_table(
        table_name="test_table",
        column_value_mappings={
            "pet_name": "George",
            "species": "Monkey",
        },
        column_to_return="id",
    )

    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name", "species"],
        where_mappings=[WhereMapping(column="id", value=id)],
    )

    assert results == [
        {"pet_name": "George", "species": "Monkey"},
    ]


def test_create_entry_in_table_no_return_columns(live_database_client, test_table_data):
    id = live_database_client._create_entry_in_table(
        table_name="test_table",
        column_value_mappings={
            "pet_name": "George",
            "species": "Monkey",
        },
    )

    assert id is None

    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Monkey")],
    )

    assert results == [
        {"pet_name": "George"},
    ]


def test_get_approved_data_sources(live_database_client: DatabaseClient):
    # Add new data sources and agencies to the database, at least two approved and one unapproved
    insert_test_agencies_and_sources_if_not_exist(
        live_database_client.connection.cursor()
    )

    # Fetch the data sources with the DatabaseClient method
    data_sources = live_database_client.get_approved_data_sources()

    # Confirm only all approved data sources are retrieved
    NUMBER_OF_DATA_SOURCE_COLUMNS = 42
    assert len(data_sources) > 0
    assert len(data_sources[0]) == NUMBER_OF_DATA_SOURCE_COLUMNS

def test_delete_from_table(live_database_client, test_table_data):
    initial_results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
    )

    assert initial_results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Jimbo"},
        {"pet_name": "Simon"},
    ]


    live_database_client._delete_from_table(
        table_name="test_table",
        id_column_name="species",
        id_column_value="Cat",
    )

    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
    )

    assert results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Simon"},
    ]

def test_update_entry_in_table(live_database_client: DatabaseClient, test_table_data):
    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Cat")],
    )

    assert results == [
        {"pet_name": "Jimbo"},
    ]

    live_database_client._update_entry_in_table(
        table_name="test_table",
        entry_id="Jimbo",
        column_edit_mappings={"species": "Lion"},
        id_column_name="pet_name",
    )


    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Cat")],
    )

    assert results == []

    results = live_database_client._select_from_single_relation(
        relation="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Lion")],
    )

    assert results == [
        {"pet_name": "Jimbo"},
    ]

def test_get_data_sources_for_map(live_database_client):
    # Add at least two new data sources to the database
    insert_test_agencies_and_sources_if_not_exist(
        live_database_client.connection.cursor()
    )
    # Fetch the data source with the DatabaseClient method
    results = live_database_client.get_data_sources_for_map()
    # Confirm both data sources are retrieved and only the proper columns are returned
    found_source = False
    for result in results:
        if result.data_source_name != "Source 1":
            continue
        found_source = True
        assert result.lat == 30
        assert result.lng == 20
    assert found_source


def test_get_agencies_from_page(live_database_client: DatabaseClient):
    results = live_database_client.get_agencies_from_page(2)

    assert len(results) > 0


def test_get_offset():
    # Send a page number to the DatabaseClient method
    # Confirm that the correct offset is returned
    assert DatabaseClient.get_offset(page=3) == 200


def test_get_data_sources_to_archive(live_database_client: DatabaseClient):
    results = live_database_client.get_data_sources_to_archive()
    assert len(results) > 0


def test_update_last_cached(live_database_client: DatabaseClient):
    # Add a new data source to the database
    insert_test_agencies_and_sources_if_not_exist(
        live_database_client.connection.cursor()
    )
    # Update the data source's last_cached value with the DatabaseClient method
    new_last_cached = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    live_database_client.update_last_cached("SOURCE_UID_1", new_last_cached)

    # Fetch the data source from the database to confirm the change
    result = live_database_client._select_from_single_relation(
        relation="data_sources_archive_info",
        columns=["last_cached"],
        where_mappings=[WhereMapping(column="airtable_uid", value="SOURCE_UID_1")],
    )[0]

    assert result["last_cached"].strftime("%Y-%m-%d %H:%M:%S") == new_last_cached


def test_get_quick_search_results(live_database_client: DatabaseClient):
    # Add new data sources to the database, some that satisfy the search criteria and some that don't
    test_datetime = live_database_client.execute_raw_sql(query="SELECT NOW()")[0]

    insert_test_agencies_and_sources_if_not_exist(
        live_database_client.connection.cursor()
    )

    # Fetch the search results using the DatabaseClient method
    result = live_database_client.get_quick_search_results(
        search="Source 1", location="City A"
    )

    assert len(result) == 1
    assert result[0].id == "SOURCE_UID_1"


def test_add_quick_search_log(live_database_client: DatabaseClient):
    # Add a quick search log to the database using the DatabaseClient method
    search = f"{uuid.uuid4().hex} QSL"
    location = "City QSL"
    live_database_client.add_quick_search_log(
        data_sources_count=1,
        processed_data_source_matches=live_database_client.DataSourceMatches(
            converted=[search],
            ids=["SOURCE_UID_QSL"],
        ),
        processed_search_parameters=live_database_client.SearchParameters(
            search=search, location=location
        ),
    )

    # Fetch the quick search logs to confirm it was added successfully
    rows = live_database_client.execute_raw_sql(
        query="""
        select search, location, results, result_count
        from quick_search_query_logs
        where search = %s and location = %s
        """,
        vars=(search, location),
    )

    assert len(rows) == 1
    row = rows[0]
    assert type(row) == dict
    assert row["search"] == search
    assert row["location"] == location
    assert row["results"][0] == "SOURCE_UID_QSL"
    assert row["result_count"] == 1


def test_get_user_info(live_database_client):
    # Add a new user to the database
    email = uuid.uuid4().hex
    password_digest = uuid.uuid4().hex

    live_database_client.add_new_user(
        email=email,
        password_digest=password_digest,
    )

    # Fetch the user using its email with the DatabaseClient method
    user_info = live_database_client.get_user_info(email=email)
    # Confirm the user is retrieved successfully
    assert user_info.password_digest == password_digest
    # Attempt to fetch non-existant user
    # Assert UserNotFoundError is raised
    with pytest.raises(UserNotFoundError):
        live_database_client.get_user_info(email="invalid_email")


def test_get_user_by_api_key(live_database_client: DatabaseClient):
    # Add a new user to the database
    test_email = uuid.uuid4().hex
    test_api_key = uuid.uuid4().hex

    user_id = live_database_client.add_new_user(
        email=test_email,
        password_digest="test_password",
    )

    # Add a role and api_key to the user
    live_database_client.execute_sqlalchemy(
        lambda: update(User)
        .where(User.email == test_email)
        .values(role="test_role", api_key=test_api_key)
    )

    # Fetch the user's role using its api key with the DatabaseClient method
    user_identifiers = live_database_client.get_user_by_api_key(api_key=test_api_key)

    # Confirm the user_id is retrieved successfully
    assert user_identifiers.id == user_id


def test_get_typeahead_suggestion(live_database_client):
    # Insert test data into the database
    cursor = live_database_client.connection.cursor()
    setup_get_typeahead_suggestion_test_data(cursor)

    # Call the get_typeahead_suggestion function
    results = live_database_client.get_typeahead_suggestions(search_term="xyl")

    # Check that the results are as expected
    assert len(results) == 3

    assert results[0].display_name == "Xylodammerung"
    assert results[0].type == "Locality"
    assert results[0].state == "Xylonsylvania"
    assert results[0].county == "Arxylodon"
    assert results[0].locality == "Xylodammerung"

    assert results[1].display_name == "Xylonsylvania"
    assert results[1].type == "State"
    assert results[1].state == "Xylonsylvania"
    assert results[1].county is None
    assert results[1].locality is None

    assert results[2].display_name == "Arxylodon"
    assert results[2].type == "County"
    assert results[2].state == "Xylonsylvania"
    assert results[2].county == "Arxylodon"
    assert results[2].locality is None


def test_search_with_location_and_record_types_real_data(live_database_client):
    """
    Due to the large number of combinations, I will refer to tests using certain parameters by their first letter
    e.g. S=State, R=Record type, L=Locality, C=County
    In the absence of a large slew of test records, I will begin by testing that
    1) Each search returns a nonzero result count
    2) SRLC search returns the fewest results
    3) S search returns the most results
    4) SR returns less results than S but more than SRC
    5) SC returns less results than S but more than SCL
    :param live_database_client:
    :return:
    """
    state_parameter = "PeNnSylvaNia"  # Additionally testing for case-insensitivity
    record_type_parameter = RecordCategories.AGENCIES
    county_parameter = "ALLEGHENY"
    locality_parameter = "pittsburgh"

    SRLC = len(
        live_database_client.search_with_location_and_record_type(
            state=state_parameter,
            record_categories=[record_type_parameter],
            county=county_parameter,
            locality=locality_parameter,
        )
    )
    S = len(
        live_database_client.search_with_location_and_record_type(state=state_parameter)
    )
    SR = len(
        live_database_client.search_with_location_and_record_type(
            state=state_parameter, record_categories=[record_type_parameter]
        )
    )
    SRC = len(
        live_database_client.search_with_location_and_record_type(
            state=state_parameter,
            record_categories=[record_type_parameter],
            county=county_parameter,
        )
    )
    SCL = len(
        live_database_client.search_with_location_and_record_type(
            state=state_parameter, county=county_parameter, locality=locality_parameter
        )
    )
    SC = len(
        live_database_client.search_with_location_and_record_type(
            state=state_parameter, county=county_parameter
        )
    )

    assert SRLC > 0
    assert SRLC < SRC
    assert SRLC < SCL
    assert S > SR > SRC
    assert S > SC > SCL


def test_search_with_location_and_record_types_real_data_multiple_records(
    live_database_client,
):
    state_parameter = "Pennsylvania"
    record_types = []
    last_count = 0

    # Check that when more record types are added, the number of results increases
    for record_type in [e for e in RecordCategories]:
        record_types.append(record_type)
        results = live_database_client.search_with_location_and_record_type(
            state=state_parameter, record_categories=record_types
        )
        assert len(results) > last_count
        last_count = len(results)

    # Finally, check that all record_types is equivalent to no record types in terms of number of results
    results = live_database_client.search_with_location_and_record_type(
        state=state_parameter
    )
    assert len(results) == last_count


def test_get_user_permissions_default(live_database_client):
    test_user = create_test_user_db_client(live_database_client)
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 0


def test_add_user_permission(live_database_client):

    # Create test user
    test_user = create_test_user_db_client(live_database_client)

    # Add permission
    live_database_client.add_user_permission(test_user.email, PermissionsEnum.DB_WRITE)
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 1


def test_remove_user_permission(live_database_client):
    test_user = create_test_user_db_client(live_database_client)

    # Add permission
    live_database_client.add_user_permission(
        test_user.email, PermissionsEnum.READ_ALL_USER_INFO
    )
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 1

    # Remove permission
    live_database_client.remove_user_permission(
        test_user.email, PermissionsEnum.READ_ALL_USER_INFO
    )
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 0


def test_get_permitted_columns(live_database_client):

    insert_test_column_permission_data(live_database_client)

    results = live_database_client.get_permitted_columns(
        relation="test_relation",
        role=RelationRoleEnum.STANDARD,
        column_permission=ColumnPermissionEnum.READ,
    )
    assert len(results) == 2
    assert "column_a" in results
    assert "column_b" in results

    results = live_database_client.get_permitted_columns(
        relation="test_relation",
        role=RelationRoleEnum.OWNER,
        column_permission=ColumnPermissionEnum.READ,
    )
    assert len(results) == 2
    assert "column_a" in results
    assert "column_b" in results

    results = live_database_client.get_permitted_columns(
        relation="test_relation",
        role=RelationRoleEnum.ADMIN,
        column_permission=ColumnPermissionEnum.WRITE,
    )
    assert len(results) == 2
    assert "column_a" in results
    assert "column_b" in results


def test_get_data_requests_for_creator(live_database_client: DatabaseClient):
    test_user = create_test_user_db_client(live_database_client)
    submission_notes_list = [uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex]

    for submission_notes in submission_notes_list:
        live_database_client.create_data_request(
            column_value_mappings={
                "submission_notes": submission_notes,
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
            "creator_user_id": test_user.user_id,
        }
    )

    results = live_database_client.user_is_creator_of_data_request(
        user_id=test_user.user_id, data_request_id=data_request_id
    )
    assert results is True

    # Test with entry where user is not listed as creator
    data_request_id = live_database_client.create_data_request(
        column_value_mappings={"submission_notes": submission_notes}
    )

    results = live_database_client.user_is_creator_of_data_request(
        user_id=test_user.user_id, data_request_id=data_request_id
    )
    assert results is False


def test_get_column_permissions_as_permission_table(live_database_client):
    insert_test_column_permission_data(live_database_client)

    results = live_database_client.get_column_permissions_as_permission_table(
        relation="test_relation"
    )
    assert results == [
        {
            "associated_column": "column_a",
            "STANDARD": "READ",
            "OWNER": "READ",
            "ADMIN": "WRITE",
        },
        {
            "associated_column": "column_b",
            "STANDARD": "READ",
            "OWNER": "WRITE",
            "ADMIN": "WRITE",
        },
        {
            "associated_column": "column_c",
            "STANDARD": "NONE",
            "OWNER": "NONE",
            "ADMIN": "READ",
        },
    ]


def test_get_agencies_without_homepage_urls(live_database_client):
    submitted_name = create_agency_entry_for_search_cache(
        db_client=live_database_client
    )

    results = live_database_client.get_agencies_without_homepage_urls()
    assert len(results) > 1
    assert results[0]["submitted_name"] == submitted_name
    assert list(results[0].keys()) == [
        "submitted_name",
        "jurisdiction_type",
        "state_iso",
        "municipality",
        "county_name",
        "airtable_uid",
        "count_data_sources",
        "zip_code",
        "no_web_presence",
    ]


def test_create_search_cache_entry(live_database_client):
    submitted_name = create_agency_entry_for_search_cache(
        db_client=live_database_client
    )

    result_to_update = live_database_client.get_agencies_without_homepage_urls()[0]

    airtable_uid = result_to_update["airtable_uid"]

    fake_search_result = "found_results"
    live_database_client.create_search_cache_entry(
        column_value_mappings={
            "agency_airtable_uid": airtable_uid,
            "search_result": fake_search_result,
        }
    )

    # Check the first result is now different
    new_result = live_database_client.get_agencies_without_homepage_urls()[0]
    assert new_result["airtable_uid"] != airtable_uid


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
