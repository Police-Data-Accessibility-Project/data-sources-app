"""
Module for testing database client functionality against a live database
"""

import uuid
from datetime import datetime

import pytest
import sqlalchemy
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from db.client.core import DatabaseClient
from db.db_client_dataclasses import (
    OrderByParameters,
    WhereMapping,
)
from db.helpers import get_offset
from db.subquery_logic import SubqueryParameterManager
from db.enums import (
    ExternalAccountTypeEnum,
    SortOrder,
    RequestStatus,
    ApprovalStatus,
)
from middleware.constants import DATETIME_FORMAT
from middleware.exceptions import (
    UserNotFoundError,
    DuplicateUserError,
)
from db.models.implementations.core.user.core import User
from db.models.implementations.core.external_account import ExternalAccount
from db.models.table_reference import SQL_ALCHEMY_TABLE_REFERENCE
from middleware.enums import PermissionsEnum, Relations, RecordTypes
from tests.helper_scripts.common_test_data import (
    get_random_number_for_testing,
    get_test_name,
)
from tests.helper_scripts.complex_test_data_creation_functions import (
    create_data_source_entry_for_url_duplicate_checking,
)

from tests.helper_scripts.helper_classes.AnyOrder import AnyOrder
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import (
    TestDataCreatorDBClient,
)
from tests.helper_scripts.test_dataclasses import TestDataRequestInfo
from tests.helper_scripts.helper_functions_complex import (
    setup_get_typeahead_suggestion_test_data,
    create_test_user_db_client,
)
from utilities.enums import RecordCategories


def test_add_new_user(live_database_client: DatabaseClient):
    fake_email = get_test_name()
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

    assert password_digest == "test_password"

    # Adding same user should produce a DuplicateUserError
    with pytest.raises(DuplicateUserError):
        live_database_client.create_new_user(fake_email, "test_password")


def test_get_user_id(live_database_client: DatabaseClient):
    # Add a new user to the database
    fake_email = get_test_name()
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
    fake_email = get_test_name()
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
    fake_email = get_test_name()
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


def test_reset_token_logic(live_database_client: DatabaseClient):
    fake_email = get_test_name()
    fake_token = uuid.uuid4().hex
    user_id = live_database_client.create_new_user(fake_email, "test_password")
    live_database_client.add_reset_token(user_id, fake_token)
    reset_token_info = live_database_client.get_reset_token_info(fake_token)
    assert reset_token_info, "Token not found"
    assert reset_token_info.user_id == user_id, "User id does not match"

    live_database_client.delete_reset_token(user_id, fake_token)
    reset_token_info = live_database_client.get_reset_token_info(fake_token)
    assert reset_token_info is None, "Token not deleted"


def test_update_user_api_key(live_database_client: DatabaseClient):
    # Add a new user to the database
    email = get_test_name()
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
    live_database_client: DatabaseClient, test_table_data
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


def test_get_data_sources_for_map(
    live_database_client,
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    tdc = test_data_creator_db_client
    location_id = tdc.locality()
    ds_id = tdc.data_source(
        approval_status=ApprovalStatus.APPROVED, record_type_id=1
    ).id
    a_id = tdc.agency(
        location_id=location_id,
        lat=0.0,
        lng=0.0,
    ).id
    tdc.link_data_source_to_agency(
        data_source_id=ds_id,
        agency_id=a_id,
    )
    results = live_database_client.get_data_sources_for_map()
    assert len(results) > 0
    assert isinstance(results[0], live_database_client.MapInfo)
    assert results[0].location_id == location_id


def test_get_offset():
    # Send a page number to the DatabaseClient method
    # Confirm that the correct offset is returned
    assert get_offset(page=3) == 200


def test_get_data_sources_to_archive(
    test_data_creator_db_client: TestDataCreatorDBClient,
    live_database_client: DatabaseClient,
):
    data_source_id = test_data_creator_db_client.data_source(
        approval_status=ApprovalStatus.APPROVED, source_url="http://example.com"
    ).id
    live_database_client._update_entry_in_table(
        table_name=Relations.DATA_SOURCES_ARCHIVE_INFO.value,
        entry_id=data_source_id,
        id_column_name="data_source_id",
        column_edit_mappings={
            "update_frequency": "Monthly",
        },
    )
    results = live_database_client.get_data_sources_to_archive()
    assert len(results) > 0


def test_update_last_cached(
    test_data_creator_db_client: TestDataCreatorDBClient,
    live_database_client: DatabaseClient,
):
    tdc = test_data_creator_db_client
    # Add a new data source to the database
    ds_info = tdc.data_source()
    # Update the data source's last_cached value with the DatabaseClient method
    new_last_cached = datetime.now().strftime(DATETIME_FORMAT)
    live_database_client.update_last_cached(
        data_source_id=ds_info.id, last_cached=new_last_cached
    )

    # Fetch the data source from the database to confirm the change
    result = live_database_client._select_from_relation(
        relation_name=Relations.DATA_SOURCES_ARCHIVE_INFO.value,
        columns=["last_cached"],
        where_mappings=[WhereMapping(column="data_source_id", value=ds_info.id)],
    )[0]

    assert result["last_cached"].strftime(DATETIME_FORMAT) == new_last_cached


def test_get_user_info(live_database_client):
    # Add a new user to the database
    email = get_test_name()
    password_digest = uuid.uuid4().hex

    live_database_client.create_new_user(
        email=email,
        password_digest=password_digest,
    )

    # Fetch the user using its email with the DatabaseClient method
    user_info = live_database_client.get_user_info(user_email=email)
    # Confirm the user is retrieved successfully
    assert user_info.password_digest == password_digest
    # Attempt to fetch non-existant user
    # Assert UserNotFoundError is raised
    with pytest.raises(UserNotFoundError):
        live_database_client.get_user_info(user_email="invalid_email")


def test_get_user_by_api_key(live_database_client: DatabaseClient):
    # Add a new user to the database
    test_email = get_test_name()
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

    assert results[0]["display_name"] == "Xylodammerung, Arxylodon, Xylonsylvania"
    assert results[0]["type"] == "Locality"
    assert results[0]["state_name"] == "Xylonsylvania"
    assert results[0]["county_name"] == "Arxylodon"
    assert results[0]["locality_name"] == "Xylodammerung"

    assert results[1]["display_name"] == "Xylonsylvania"
    assert results[1]["type"] == "State"
    assert results[1]["state_name"] == "Xylonsylvania"
    assert results[1]["county_name"] is None
    assert results[1]["locality_name"] is None

    assert results[2]["display_name"] == "Arxylodon, Xylonsylvania"
    assert results[2]["type"] == "County"
    assert results[2]["state_name"] == "Xylonsylvania"
    assert results[2]["county_name"] == "Arxylodon"
    assert results[2]["locality_name"] is None


def test_get_typeahead_agencies(live_database_client):
    # Insert test data into the database
    cursor = live_database_client.connection.cursor()
    setup_get_typeahead_suggestion_test_data(cursor)

    results = live_database_client.get_typeahead_agencies(search_term="xyl")
    assert len(results) > 0
    assert results[0]["display_name"] == "Xylodammerung Police Agency"
    assert results[0]["jurisdiction_type"] == "state"
    assert results[0]["state_iso"] == "XY"
    assert results[0]["county_name"] == "Arxylodon"
    assert results[0]["locality_name"] == "Xylodammerung"


def test_search_with_location_and_record_types_real_data(
    test_data_creator_db_client: TestDataCreatorDBClient, live_database_client
):
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
    state_parameter = "Pennsylvania"  # Additionally testing for case-insensitivity
    record_type_parameter = RecordCategories.AGENCIES
    county_parameter = "Allegheny"
    locality_parameter = "Pittsburgh"

    tdc = test_data_creator_db_client
    pennsylvania_location_id = live_database_client.get_location_id(
        where_mappings={"state_name": "Pennsylvania", "county_name": None}
    )
    allegheny_location_id = live_database_client.get_location_id(
        where_mappings={
            "state_name": "Pennsylvania",
            "county_name": "Allegheny",
            "locality_name": None,
        }
    )
    philadelphia_county_location_id = live_database_client.get_location_id(
        where_mappings={
            "state_name": "Pennsylvania",
            "county_name": "Philadelphia",
            "locality_name": None,
        }
    )
    try:
        pittsburgh_location_id = tdc.locality(locality_name="Pittsburgh")
    except IntegrityError:
        pittsburgh_location_id = tdc.db_client.get_location_id(
            where_mappings={
                "state_name": "Pennsylvania",
                "county_name": "Allegheny",
                "locality_name": "Pittsburgh",
            }
        )
    secondary_location_id = tdc.locality()

    def agency_and_data_source(
        location_id, record_type: RecordTypes = RecordTypes.LIST_OF_DATA_SOURCES
    ):
        record_type_id = live_database_client.get_record_type_id_by_name(
            record_type.value
        )
        ds_id = tdc.data_source(
            approval_status=ApprovalStatus.APPROVED, record_type_id=record_type_id
        ).id
        a_id = tdc.agency(location_id=location_id).id
        tdc.link_data_source_to_agency(data_source_id=ds_id, agency_id=a_id)

    # State
    agency_and_data_source(pennsylvania_location_id)
    agency_and_data_source(
        pennsylvania_location_id, record_type=RecordTypes.RECORDS_REQUEST_INFO
    )
    # Counties
    agency_and_data_source(allegheny_location_id)
    agency_and_data_source(philadelphia_county_location_id)
    # Localities
    agency_and_data_source(pittsburgh_location_id)
    agency_and_data_source(secondary_location_id)
    agency_and_data_source(
        pittsburgh_location_id, record_type=RecordTypes.RECORDS_REQUEST_INFO
    )

    def search(state, record_categories=None, county=None, locality=None):
        location_id = live_database_client.get_location_id(
            where_mappings={
                "state_name": state,
                "county_name": county,
                "locality_name": locality,
            }
        )
        if record_categories is not None:
            additional_kwargs = {"record_categories": record_categories}
        else:
            additional_kwargs = {}
        return live_database_client.search_with_location_and_record_type(
            location_id=location_id, **additional_kwargs
        )

    SRLC = len(
        search(
            state=state_parameter,
            record_categories=[record_type_parameter],
            county=county_parameter,
            locality=locality_parameter,
        )
    )
    S = len(search(state=state_parameter))
    SR = len(search(state=state_parameter, record_categories=[record_type_parameter]))
    SRC = len(
        search(
            state=state_parameter,
            record_categories=[record_type_parameter],
            county=county_parameter,
        )
    )
    SCL = len(
        search(
            state=state_parameter, county=county_parameter, locality=locality_parameter
        )
    )
    SC = len(search(state=state_parameter, county=county_parameter))

    assert SRLC > 0
    assert SRLC < SRC
    assert SRLC < SCL
    assert S > SR > SRC
    assert S > SC > SCL


def test_search_with_location_and_record_types_real_data_multiple_records(
    test_data_creator_db_client,
    live_database_client,
):
    pa_location_id = live_database_client.get_location_id(
        where_mappings={
            "state_name": "Pennsylvania",
            "county_name": None,
            "locality_name": None,
        }
    )
    tdc = test_data_creator_db_client

    def agency_and_data_source(
        location_id, record_type: RecordTypes = RecordTypes.LIST_OF_DATA_SOURCES
    ):
        record_type_id = live_database_client.get_record_type_id_by_name(
            record_type.value
        )
        ds_id = tdc.data_source(
            approval_status=ApprovalStatus.APPROVED, record_type_id=record_type_id
        ).id
        a_id = tdc.agency(location_id=location_id).id
        tdc.link_data_source_to_agency(data_source_id=ds_id, agency_id=a_id)

    record_types = [record_type for record_type in RecordTypes]
    for record_type in record_types:
        agency_and_data_source(pa_location_id, record_type=record_type)

    record_categories = []
    last_count = 0
    # Exclude the ALL pseudo-category
    applicable_record_categories = [
        e for e in RecordCategories if e != RecordCategories.ALL
    ]

    # Check that when more record types are added, the number of results increases
    for record_category in applicable_record_categories:
        record_categories.append(record_category)
        results = live_database_client.search_with_location_and_record_type(
            location_id=pa_location_id, record_categories=record_categories
        )
        assert (
            len(results) > last_count
        ), f"{record_category} failed (total record_categories: {len(record_categories)})"
        last_count = len(results)

    # Finally, check that all record_types is equivalent to no record types in terms of number of results
    results = live_database_client.search_with_location_and_record_type(
        location_id=pa_location_id
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
    live_database_client.add_user_permission(
        test_user.user_id, PermissionsEnum.DB_WRITE
    )
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 1


def test_remove_user_permission(live_database_client):
    test_user = create_test_user_db_client(live_database_client)

    # Add permission
    live_database_client.add_user_permission(
        test_user.user_id, PermissionsEnum.READ_ALL_USER_INFO
    )
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 1

    # Remove permission
    live_database_client.remove_user_permission(
        test_user.user_id, PermissionsEnum.READ_ALL_USER_INFO
    )
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 0


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
        rc_ids: list[int], record_categories: list[RecordCategories]
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
        record_categories=RecordCategories.ALL,
    )

    # Confirm record exists in both `recent_searches` and `link_recent_search_record_types` tables
    recent_search_results = get_recent_searches()
    assert len(recent_search_results) == 1

    link_results = get_link_recent_search_record_types(recent_search_results[0]["id"])

    assert len(link_results) == 1

    # Confirm record category is all
    assert_are_expected_record_categories(
        rc_ids=[link_results[0]["record_category_id"]],
        record_categories=[RecordCategories.ALL],
    )

    tdc.db_client.create_search_record(
        user_id=user_info.id,
        location_id=location_id,
        record_categories=[RecordCategories.AGENCIES, RecordCategories.JAIL],
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
        record_categories=[RecordCategories.AGENCIES, RecordCategories.JAIL],
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
