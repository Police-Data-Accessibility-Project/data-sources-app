import json
import uuid
from datetime import datetime, timezone, timedelta

import psycopg2
import pytest

from database_client.database_client import DatabaseClient
from database_client.result_formatter import ResultFormatter
from middleware.custom_exceptions import (
    AccessTokenNotFoundError,
    UserNotFoundError,
    TokenNotFoundError,
)
from tests.fixtures import live_database_client, dev_db_connection, db_cursor
from tests.helper_functions import (
    insert_test_agencies_and_sources,
    insert_test_agencies_and_sources_if_not_exist,
)


def test_add_new_user(live_database_client):
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    cursor = live_database_client.cursor
    cursor.execute(f"SELECT password_digest FROM users WHERE email = %s", (fake_email,))
    password_digest = cursor.fetchone()[0]

    assert password_digest == "test_password"


def test_get_user_id(live_database_client):
    # Add a new user to the database
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")

    # Directly fetch the user ID from the database for comparison
    cursor = live_database_client.cursor
    cursor.execute(f"SELECT id FROM users WHERE email = %s", (fake_email,))
    direct_user_id = cursor.fetchone()[0]

    # Get the user ID from the live database
    result_user_id = live_database_client.get_user_id(fake_email)

    # Compare the two user IDs
    assert result_user_id == direct_user_id


def test_set_user_password_digest(live_database_client):
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    live_database_client.set_user_password_digest(fake_email, "test_password")
    cursor = live_database_client.cursor
    cursor.execute(f"SELECT password_digest FROM users WHERE email = %s", (fake_email,))
    password_digest = cursor.fetchone()[0]

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

    user_info = live_database_client.get_user_info(email)
    assert user_info.api_key is None

    # Update the user's API key with the DatabaseClient Method
    live_database_client.update_user_api_key(
        api_key="test_api_key", user_id=user_info.id
    )

    # Fetch the user's API key from the database to confirm the change
    user_info = live_database_client.get_user_info(email)
    assert user_info.api_key == "test_api_key"


def test_get_data_source_by_id(live_database_client):
    # Add a new data source and agency to the database
    insert_test_agencies_and_sources_if_not_exist(live_database_client.cursor)
    # Fetch the data source using its id with the DatabaseClient method
    result = live_database_client.get_data_source_by_id("SOURCE_UID_1")

    # Confirm the data source and agency are retrieved successfully
    NUMBER_OF_RESULT_COLUMNS = 67
    assert result is not None
    assert len(result) == NUMBER_OF_RESULT_COLUMNS
    assert result[0] == "Source 1"


def test_get_approved_data_sources(live_database_client):
    # Add new data sources and agencies to the database, at least two approved and one unapproved
    insert_test_agencies_and_sources_if_not_exist(live_database_client.cursor)

    # Fetch the data sources with the DatabaseClient method
    data_sources = live_database_client.get_approved_data_sources()

    # Confirm only all approved data sources are retrieved
    NUMBER_OF_DATA_SOURCE_COLUMNS = 42
    assert len(data_sources) > 0
    assert len(data_sources[0]) == NUMBER_OF_DATA_SOURCE_COLUMNS


def test_get_needs_identification_data_sources(live_database_client):
    # Add new data sources to the database, at least two labeled 'needs identification' and one not
    insert_test_agencies_and_sources_if_not_exist(live_database_client.cursor)
    # Fetch the data sources with the DatabaseClient method
    results = live_database_client.get_needs_identification_data_sources()

    found = False
    for result in results:
        # Confirm "Source 2" (which was inserted as "needs identification" is retrieved).
        if result[0] != "Source 2":
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
    live_database_client.cursor.execute(
        "SELECT * FROM data_sources WHERE name = %s", (name,)
    )

    results = live_database_client.cursor.fetchall()

    assert len(results) == 1


def test_update_data_source(live_database_client):
    # Add a new data source to the database
    insert_test_agencies_and_sources_if_not_exist(live_database_client.cursor)

    # Update the data source with the DatabaseClient method
    new_description = uuid.uuid4().hex
    live_database_client.update_data_source(
        {"description": new_description}, "SOURCE_UID_1"
    )

    # Fetch the data source from the database to confirm the change
    result = live_database_client.get_data_source_by_id("SOURCE_UID_1")

    assert result[2] == new_description


def test_get_data_sources_for_map(live_database_client):
    # Add at least two new data sources to the database
    insert_test_agencies_and_sources_if_not_exist(live_database_client.cursor)
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
    insert_test_agencies_and_sources_if_not_exist(live_database_client.cursor)
    # Update the data source's last_cached value with the DatabaseClient method
    new_last_cached = datetime.now()
    live_database_client.update_last_cached("SOURCE_UID_1", new_last_cached)

    # Fetch the data source from the database to confirm the change
    result = live_database_client.get_data_source_by_id("SOURCE_UID_1")
    zipped_results = ResultFormatter.zip_get_data_source_by_id_results(result)

    assert zipped_results["last_cached"] == new_last_cached.strftime("%Y-%m-%d")


def test_get_quick_search_results(live_database_client):
    # Add new data sources to the database, some that satisfy the search criteria and some that don't
    insert_test_agencies_and_sources_if_not_exist(live_database_client.cursor)

    # Fetch the search results using the DatabaseClient method
    result = live_database_client.get_quick_search_results(
        search="Source 1", location="City A"
    )

    assert len(result) == 1
    assert result[0].id == "SOURCE_UID_1"


def test_add_quick_search_log(live_database_client):
    # Add a quick search log to the database using the DatabaseClient method
    search = "Source QSL"
    location = "City QSL"
    live_database_client.add_quick_search_log(
        data_sources_count=1,
        processed_data_source_matches=live_database_client.DataSourceMatches(
            converted=["Source QSL"],
            ids=["SOURCE_UID_QSL"],
        ),
        processed_search_parameters=live_database_client.SearchParameters(
            search=search, location=location
        ),
    )

    # Fetch the quick search logs to confirm it was added successfully
    live_database_client.cursor.execute(
        """
        select search, location, results, result_count
        from quick_search_query_logs
        where search = %s and location = %s
        """,
        (search, location),
    )
    rows = live_database_client.cursor.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == search
    assert rows[0][1] == location
    assert rows[0][2][0] == "SOURCE_UID_QSL"
    assert rows[0][3] == 1


def test_add_new_access_token(live_database_client):
    # Call the DatabaseClient method to generate and add a new access token to the database
    access_token = uuid.uuid4().hex
    expiration_date = datetime.now(tz=timezone.utc)

    live_database_client.add_new_access_token(
        token=access_token,
        expiration=expiration_date,
    )

    live_database_client.cursor.execute(
        f"select token, expiration_date from access_tokens where token = '{access_token}'"
    )

    # Fetch the new access token from the database to confirm it was added successfully
    results = live_database_client.cursor.fetchone()
    assert results[0] == access_token
    assert results[1] == expiration_date


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


def test_get_role_by_email(live_database_client):
    # Add a new user to the database
    live_database_client.add_new_user(
        email="test_user",
        password_digest="test_password",
    )

    # Add a role to the user
    live_database_client.cursor.execute(
        "update users set role = 'test_role' where email = 'test_user'",
    )

    # Fetch the user using its email with the DatabaseClient method
    role_info = live_database_client.get_role_by_email(email="test_user")

    # Confirm the role is retrieved successfully
    assert role_info.role == "test_role"


def test_add_new_session_token(live_database_client):
    # Add a new user to the database
    email = uuid.uuid4().hex
    live_database_client.add_new_user(
        email=email,
        password_digest="test_password",
    )

    # Create a new session token locally
    session_token = uuid.uuid4().hex

    # Call the DatabaseClient method add the session token to the database
    live_database_client.add_new_session_token(
        session_token=session_token,
        email=email,
        expiration=datetime.now(tz=timezone.utc),
    )

    # Fetch the new session token from the database to confirm it was added successfully
    result = live_database_client.get_session_token_info(api_key=session_token)

    assert result.email == email


def test_delete_session_token(live_database_client):
    # Create new user
    email = uuid.uuid4().hex
    live_database_client.add_new_user(
        email=email,
        password_digest="test_password",
    )

    # Add a session token to the database associated with the user
    session_token = uuid.uuid4().hex
    live_database_client.add_new_session_token(
        session_token=session_token,
        email=email,
        expiration=datetime.now(tz=timezone.utc),
    )

    # Confirm session token exists beforehand:
    result = live_database_client.get_session_token_info(api_key=session_token)
    assert result.email == email

    # Delete the session token with the DatabaseClient method
    live_database_client.delete_session_token(old_token=session_token)

    # Confirm the session token was deleted by attempting to fetch it
    assert live_database_client.get_session_token_info(session_token) is None



def test_get_access_token(live_database_client):
    # Add a new access token to the database
    live_database_client.add_new_access_token(
        token="test_access_token",
        expiration=datetime.now(tz=timezone.utc),
    )

    # Fetch the access token using the DatabaseClient method
    access_token = live_database_client.get_access_token(api_key="test_access_token")

    # Confirm that the access token is retrieved
    assert access_token.token == "test_access_token"

    # Attempt to fetch a non-existant access token
    # Assert AccessTokenNotFoundError is raised
    with pytest.raises(AccessTokenNotFoundError):
        live_database_client.get_access_token(api_key="non_existant_access_token")


def test_delete_expired_access_tokens(live_database_client):
    # Add new access tokens to the database, at least two expired and one unexpired
    expired_tokens = [uuid.uuid4().hex for _ in range(2)]
    unexpired_token = uuid.uuid4().hex
    for token in expired_tokens:
        live_database_client.add_new_access_token(
            token=token,
            expiration=datetime.now(tz=timezone.utc) - timedelta(days=1),
        )
    live_database_client.add_new_access_token(
        token=unexpired_token,
        expiration=datetime.now(tz=timezone.utc) + timedelta(days=1),
    )

    # Delete the expired access tokens using the DatabaseClient method
    live_database_client.delete_expired_access_tokens()

    # Confirm that only the expired access tokens were deleted and that all expired tokens were deleted
    for token in expired_tokens:
        with pytest.raises(AccessTokenNotFoundError):
            live_database_client.get_access_token(api_key=token)
    assert live_database_client.get_access_token(api_key=unexpired_token)
