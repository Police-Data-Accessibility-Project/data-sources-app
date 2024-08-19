"""
Module for testing database client functionality against a live database
"""

import uuid
from datetime import datetime, timezone, timedelta

from psycopg2.extras import DictRow
import pytest

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from database_client.result_formatter import ResultFormatter
from middleware.custom_exceptions import (
    AccessTokenNotFoundError,
    UserNotFoundError,
)
from middleware.enums import PermissionsEnum
from tests.fixtures import (
    live_database_client,
    dev_db_connection,
    bypass_api_key_required,
    db_cursor,
)
from tests.helper_scripts.helper_functions import (
    insert_test_agencies_and_sources_if_not_exist,
    setup_get_typeahead_suggestion_test_data,
    create_test_user_db_client,
)
from utilities.enums import RecordCategories


def test_add_new_user(live_database_client):
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    result = live_database_client.execute_raw_sql(
        query=f"SELECT password_digest, api_key FROM users WHERE email = %s",
        vars=(fake_email,),
    )[0]

    password_digest = result["password_digest"]
    api_key = result["api_key"]

    assert api_key is not None
    assert password_digest == "test_password"


def test_get_user_id(live_database_client):
    # Add a new user to the database
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")

    # Directly fetch the user ID from the database for comparison
    direct_user_id = live_database_client.execute_raw_sql(
        query=f"SELECT id FROM users WHERE email = %s", vars=(fake_email,)
    )[0]["id"]

    # Get the user ID from the live database
    result_user_id = live_database_client.get_user_id(fake_email)

    # Compare the two user IDs
    assert result_user_id == direct_user_id


def test_link_external_account(live_database_client):
    fake_email = uuid.uuid4().hex
    fake_external_account_id = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    user_id = live_database_client.get_user_id(fake_email)
    live_database_client.link_external_account(
        user_id=str(user_id),
        external_account_id=fake_external_account_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )
    '''cursor = live_database_client.cursor
    cursor.execute(
        f"SELECT user_id, account_type FROM external_accounts WHERE account_identifier = %s",
        (fake_external_account_id,),
    )
    row = cursor.fetchone()'''
    row = live_database_client.execute_raw_sql(
        query=f"SELECT user_id, account_type FROM external_accounts WHERE account_identifier = %s",
        vars=(fake_external_account_id,),
    )[0]

    assert row["user_id"] == user_id
    assert row["account_type"] == ExternalAccountTypeEnum.GITHUB.value


def test_get_user_info_by_external_account_id(live_database_client):
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


def test_set_user_password_digest(live_database_client):
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    live_database_client.set_user_password_digest(fake_email, "test_password")
    password_digest = live_database_client.execute_raw_sql(
        query=f"SELECT password_digest FROM users WHERE email = %s", vars=(fake_email,)
    )[0]["password_digest"]

    assert password_digest == "test_password"


def test_reset_token_logic(live_database_client):
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


def test_update_user_api_key(live_database_client):
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


def test_get_data_source_by_id(live_database_client):
    # Add a new data source and agency to the database
    insert_test_agencies_and_sources_if_not_exist(live_database_client.connection.cursor())
    # Fetch the data source using its id with the DatabaseClient method
    result = live_database_client.get_data_source_by_id("SOURCE_UID_1")

    # Confirm the data source and agency are retrieved successfully
    NUMBER_OF_RESULT_COLUMNS = 67
    assert result is not None
    assert len(result) == NUMBER_OF_RESULT_COLUMNS
    assert result["name"] == "Source 1"


def test_get_approved_data_sources(live_database_client):
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


def test_get_needs_identification_data_sources(live_database_client):
    # Add new data sources to the database, at least two labeled 'needs identification' and one not
    insert_test_agencies_and_sources_if_not_exist(
        live_database_client.connection.cursor()
    )
    # Fetch the data sources with the DatabaseClient method
    results = live_database_client.get_needs_identification_data_sources()

    found = False
    for result in results:
        # Confirm "Source 2" (which was inserted as "needs identification" is retrieved).
        if result["name"] != "Source 2":
            continue
        found = True
    assert found
    # Confirm only all data sources labeled 'needs identification' are retrieved


def test_add_new_data_source(live_database_client):
    # Add a new data source to the database with the DatabaseClient method
    name = uuid.uuid4().hex
    live_database_client.add_new_data_source(
        {
            "name": name,
            "source_url": "https://example.com",
        }
    )

    # Fetch the data source from the database to confirm that it was added successfully
    results = live_database_client.execute_raw_sql(query="SELECT * FROM data_sources WHERE name = %s", vars=(name,))

    assert len(results) == 1


def test_update_data_source(live_database_client):
    # Add a new data source to the database
    insert_test_agencies_and_sources_if_not_exist(
        live_database_client.connection.cursor()
    )

    # Update the data source with the DatabaseClient method
    new_description = uuid.uuid4().hex
    live_database_client.update_data_source(
        {"description": new_description}, "SOURCE_UID_1"
    )

    # Fetch the data source from the database to confirm the change
    result = live_database_client.get_data_source_by_id("SOURCE_UID_1")

    assert result["description"] == new_description


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


def test_get_agencies_from_page(live_database_client):
    results = live_database_client.get_agencies_from_page(2)

    assert len(results) > 0


def test_get_offset():
    # Send a page number to the DatabaseClient method
    # Confirm that the correct offset is returned
    assert DatabaseClient.get_offset(3) == 2000


def test_get_data_sources_to_archive(live_database_client):
    results = live_database_client.get_data_sources_to_archive()
    assert len(results) > 0


def test_update_last_cached(live_database_client):
    # Add a new data source to the database
    insert_test_agencies_and_sources_if_not_exist(
        live_database_client.connection.cursor()
    )
    # Update the data source's last_cached value with the DatabaseClient method
    new_last_cached = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    live_database_client.update_last_cached("SOURCE_UID_1", new_last_cached)

    # Fetch the data source from the database to confirm the change
    result = live_database_client.get_data_source_by_id("SOURCE_UID_1")
    zipped_results = ResultFormatter.zip_get_data_source_by_id_results(result)

    assert zipped_results["last_cached"] == new_last_cached


def test_get_quick_search_results(live_database_client):
    # Add new data sources to the database, some that satisfy the search criteria and some that don't
    test_datetime = live_database_client.execute_raw_sql(query="SELECT NOW()")[0]

    insert_test_agencies_and_sources_if_not_exist(live_database_client.connection.cursor())

    # Fetch the search results using the DatabaseClient method
    result = live_database_client.get_quick_search_results(
        search="Source 1", location="City A"
    )

    assert len(result) == 1
    assert result[0].id == "SOURCE_UID_1"


def test_add_quick_search_log(live_database_client):
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
    assert type(row) == DictRow
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


def test_get_user_by_api_key(live_database_client):
    # Add a new user to the database
    test_email = uuid.uuid4().hex
    test_api_key = uuid.uuid4().hex

    user_id = live_database_client.add_new_user(
        email=test_email,
        password_digest="test_password",
    )

    # Add a role and api_key to the user
    live_database_client.execute_raw_sql(
        query=f"update users set api_key = %s where email = %s",
        vars=(
            test_api_key,
            test_email,
        ),
    )

    # Fetch the user's role using its api key with the DatabaseClient method
    api_key_user_id = live_database_client.get_user_by_api_key(api_key=test_api_key)

    # Confirm the user_id is retrieved successfully
    assert api_key_user_id == user_id

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
