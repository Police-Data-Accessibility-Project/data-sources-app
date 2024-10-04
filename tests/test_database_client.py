"""
Module for testing database client functionality against a live database
"""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

import psycopg.errors
import pytest
from sqlalchemy import insert, select, update

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import (
    OrderByParameters,
    WhereMapping,
)
from database_client.subquery_logic import SubqueryParameters, SubqueryParameterManager
from database_client.enums import (
    ExternalAccountTypeEnum,
    RelationRoleEnum,
    ColumnPermissionEnum,
    SortOrder,
)
from middleware.exceptions import (
    UserNotFoundError,
    DuplicateUserError,
)
from database_client.models import (
    Agency,
    AgencySourceLink,
    DataSource,
    ExternalAccount,
    TestTable,
    User,
)
from middleware.enums import PermissionsEnum, Relations
from tests.conftest import live_database_client, test_table_data
from tests.helper_scripts.common_test_data import (
    insert_test_column_permission_data,
    create_agency_entry_for_search_cache,
    create_data_source_entry_for_url_duplicate_checking, TestDataCreator,
)
from tests.helper_scripts.helper_functions import (
    insert_test_agencies_and_sources_if_not_exist,
    setup_get_typeahead_suggestion_test_data,
    create_test_user_db_client,
)
from utilities.enums import RecordCategories
from conftest import test_data_creator, monkeysession


def test_add_new_user(live_database_client: DatabaseClient):
    fake_email = uuid.uuid4().hex
    live_database_client.create_new_user(fake_email, "test_password")
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

    # Adding same user should produce a DuplicateUserError
    with pytest.raises(DuplicateUserError):
        live_database_client.create_new_user(fake_email, "test_password")


def test_get_user_id(live_database_client: DatabaseClient):
    # Add a new user to the database
    fake_email = uuid.uuid4().hex
    live_database_client.create_new_user(fake_email, "test_password")

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
    live_database_client.create_new_user(fake_email, "test_password")
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
    live_database_client.create_new_user(fake_email, "test_password")
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
    live_database_client.create_new_user(fake_email, "test_password")
    live_database_client.set_user_password_digest(fake_email, "test_password")
    password_digest = live_database_client.execute_sqlalchemy(
        lambda: select(User.password_digest).where(User.email == fake_email)
    ).one_or_none()[0]

    assert password_digest == "test_password"


def test_reset_token_logic(live_database_client: DatabaseClient):
    fake_email = uuid.uuid4().hex
    fake_token = uuid.uuid4().hex
    live_database_client.create_new_user(fake_email, "test_password")
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

    live_database_client.create_new_user(
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


def test_select_from_relation_columns_only(
    test_table_data, live_database_client: DatabaseClient
):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
    )

    assert results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Jimbo"},
        {"pet_name": "Simon"},
    ]


def test_select_from_relation_where_mapping(
    live_database_client: DatabaseClient,
):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Aardvark")],
    )

    assert results == [
        {"pet_name": "Arthur"},
    ]

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", eq=False, value="Aardvark")],
    )

    assert results == [
        {"pet_name": "Jimbo"},
        {"pet_name": "Simon"},
    ]


def test_select_from_relation_limit(live_database_client: DatabaseClient):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        limit=1,
    )

    assert results == [
        {"pet_name": "Arthur"},
    ]


def test_select_from_relation_limit_and_offset(
    live_database_client: DatabaseClient, monkeypatch
):
    # Used alongside limit; we mock PAGE_SIZE to be one
    monkeypatch.setattr("database_client.database_client.PAGE_SIZE", 1)

    live_database_client.get_offset = MagicMock(return_value=1)

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        limit=1,
        page=1,  # 1 is the second page; 0-indexed
    )

    assert results == [
        {"pet_name": "Jimbo"},
    ]


def test_select_from_relation_order_by(live_database_client: DatabaseClient):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        order_by=OrderByParameters(sort_by="species", sort_order=SortOrder.ASCENDING),
    )

    assert results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Simon"},
        {"pet_name": "Jimbo"},
    ]


def test_select_from_relation_all_parameters(
    live_database_client: DatabaseClient, monkeypatch
):
    # Used alongside limit; we mock PAGE_SIZE to be one
    monkeypatch.setattr("database_client.database_client.PAGE_SIZE", 1)

    # Add additional row to the table to test the offset and limit
    live_database_client.execute_sqlalchemy(
        lambda: insert(TestTable).values(pet_name="Ezekiel", species="Cat")
    )

    results = live_database_client._select_from_relation(
        relation_name="test_table",
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


def test_select_from_relation_subquery(live_database_client: DatabaseClient):
    agency_id = uuid.uuid4().hex
    data_source_id = uuid.uuid4().hex
    agency_name = uuid.uuid4().hex
    data_source_name = uuid.uuid4().hex

    live_database_client.execute_sqlalchemy(
        lambda: insert(Agency).values(
            airtable_uid=agency_id, submitted_name=agency_name, jurisdiction_type="federal"
        )
    )
    live_database_client.execute_sqlalchemy(
        lambda: insert(DataSource).values(
            airtable_uid=data_source_id, name=data_source_name
        )
    )
    live_database_client.execute_sqlalchemy(
        lambda: insert(AgencySourceLink).values(
            data_source_uid=data_source_id, agency_uid=agency_id
        )
    )

    where_mappings = [WhereMapping(column="airtable_uid", value=data_source_id)]
    subquery_parameters = [
        SubqueryParameters(
            relation_name=Relations.AGENCIES_EXPANDED.value,
            columns=["airtable_uid", "name"],
            linking_column="agencies",
        )
    ]

    results = live_database_client._select_from_relation(
        relation_name="data_sources",
        columns=["airtable_uid", "name"],
        where_mappings=where_mappings,
        subquery_parameters=subquery_parameters,
    )

    assert results == [
        {
            "name": data_source_name,
            "airtable_uid": data_source_id,
            "agencies": [
                {
                    "name": agency_name,
                    "airtable_uid": agency_id,
                }
            ],
        }
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

    results = live_database_client._select_from_relation(
        relation_name="test_table",
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

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Monkey")],
    )

    assert results == [
        {"pet_name": "George"},
    ]


def test_delete_from_table(live_database_client, test_table_data):
    initial_results = live_database_client._select_from_relation(
        relation_name="test_table",
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

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
    )

    assert results == [
        {"pet_name": "Arthur"},
        {"pet_name": "Simon"},
    ]


def test_update_entry_in_table(live_database_client: DatabaseClient, test_table_data):
    results = live_database_client._select_from_relation(
        relation_name="test_table",
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

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Cat")],
    )

    assert results == []

    results = live_database_client._select_from_relation(
        relation_name="test_table",
        columns=["pet_name"],
        where_mappings=[WhereMapping(column="species", value="Lion")],
    )

    assert results == [
        {"pet_name": "Jimbo"},
    ]


def test_get_data_sources_for_map(live_database_client):
    results = live_database_client.get_data_sources_for_map()
    assert len(results) > 0
    assert isinstance(results[0], live_database_client.MapInfo)


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
    result = live_database_client._select_from_relation(
        relation_name="data_sources_archive_info",
        columns=["last_cached"],
        where_mappings=[WhereMapping(column="airtable_uid", value="SOURCE_UID_1")],
    )[0]

    assert result["last_cached"].strftime("%Y-%m-%d %H:%M:%S") == new_last_cached


def test_get_user_info(live_database_client):
    # Add a new user to the database
    email = uuid.uuid4().hex
    password_digest = uuid.uuid4().hex

    live_database_client.create_new_user(
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

    user_id = live_database_client.create_new_user(
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


def test_get_typeahead_locations(live_database_client: DatabaseClient):
    # Insert test data into the database
    cursor = live_database_client.connection.cursor()
    setup_get_typeahead_suggestion_test_data(cursor)

    # Call the get_typeahead_suggestion function
    results = live_database_client.get_typeahead_locations(search_term="xyl")

    # Check that the results are as expected
    assert len(results) == 3

    assert results[0]["display_name"] == "Xylodammerung"
    assert results[0]["type"] == "Locality"
    assert results[0]["state"] == "Xylonsylvania"
    assert results[0]["county"] == "Arxylodon"
    assert results[0]["locality"] == "Xylodammerung"

    assert results[1]["display_name"] == "Xylonsylvania"
    assert results[1]["type"] == "State"
    assert results[1]["state"] == "Xylonsylvania"
    assert results[1]["county"] is None
    assert results[1]["locality"] is None

    assert results[2]["display_name"] == "Arxylodon"
    assert results[2]["type"] == "County"
    assert results[2]["state"] == "Xylonsylvania"
    assert results[2]["county"] == "Arxylodon"
    assert results[2]["locality"] is None


def test_get_typeahead_agencies(live_database_client):
    # Insert test data into the database
    cursor = live_database_client.connection.cursor()
    setup_get_typeahead_suggestion_test_data(cursor)

    results = live_database_client.get_typeahead_agencies(search_term="xyl")
    assert len(results) == 1
    assert results[0]["display_name"] == "Xylodammerung Police Agency"
    assert results[0]["jurisdiction_type"] == "state"
    assert results[0]["state"] == "XY"
    assert results[0]["county"] == "Arxylodon"
    assert results[0]["locality"] == "Xylodammerung"


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


def test_get_permitted_columns(live_database_client: DatabaseClient):

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


def test_get_column_permissions_as_permission_table(
    live_database_client: DatabaseClient,
):
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


def test_get_related_data_sources(live_database_client):

    # Create two data sources
    source_column_value_mappings = []
    source_ids = []
    for i in range(2):
        source_column_value_mapping = {
            "airtable_uid": uuid.uuid4().hex,
            "name": uuid.uuid4().hex,
        }
        source_id = live_database_client.add_new_data_source(
            column_value_mappings=source_column_value_mapping
        )
        source_column_value_mappings.append(source_column_value_mapping)
        source_ids.append(source_id)

    # Create a request
    submission_notes = uuid.uuid4().hex
    request_id = live_database_client.create_data_request(
        column_value_mappings={"submission_notes": submission_notes}
    )

    # Associate them in the link table
    for source_id in source_ids:
        live_database_client.create_request_source_relation(
            column_value_mappings={"request_id": request_id, "source_id": source_id}
        )

    results = live_database_client.get_related_data_sources(data_request_id=request_id)

    assert len(results) == 2

    for result in results:
        assert result["name"] in [
            source["name"] for source in source_column_value_mappings
        ]


def test_create_request_source_relation(live_database_client):
    # Create data source and request

    source_id = live_database_client.add_new_data_source(
        column_value_mappings={
            "airtable_uid": uuid.uuid4().hex,
            "name": uuid.uuid4().hex,
        }
    )

    # Create a request
    request_id = live_database_client.create_data_request(
        column_value_mappings={"submission_notes": uuid.uuid4().hex}
    )

    # Try to add twice and get a unique violation
    live_database_client.create_request_source_relation(
        column_value_mappings={"request_id": request_id, "source_id": source_id}
    )
    with pytest.raises(psycopg.errors.UniqueViolation):
        live_database_client.create_request_source_relation(
            column_value_mappings={"request_id": request_id, "source_id": source_id}
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

def test_get_data_requests(test_data_creator: TestDataCreator):
    # There should be at least one data request in the DataRequests directory
    tdc = test_data_creator
    tdc.data_request(tdc.get_admin_tus())

    # Create a data request

    results = tdc.db_client.get_data_requests(
        columns=["id"],
        subquery_parameters=[SubqueryParameterManager.data_sources()]
    )
    assert results

def test_get_data_sources(live_database_client):
    results = live_database_client.get_data_sources(
        columns=["airtable_uid"],
        subquery_parameters=[SubqueryParameterManager.agencies(
            columns=["airtable_uid"],
        )]
    )
    assert results

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
