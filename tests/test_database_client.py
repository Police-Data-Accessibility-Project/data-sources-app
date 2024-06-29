import uuid

import pytest

from tests.fixtures import live_database_client, dev_db_connection, db_cursor


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

    # Update the user's API key with the DatabaseClint Method

    # Fetch the user's API key from the database to confirm the change

    pytest.fail("Test not implemented")


def test_get_data_source_by_id(live_database_client):
    # Add a new data source and agency to the database

    # Fetch the data source using its id with the DatabaseClient method

    # Confirm the data source and agency are retrieved successfully

    pytest.fail("Test not implemented")


def test_get_approved_data_sources(live_database_client):
    # Add new data sources and agencies to the database, at least two approved and one unapproved

    # Fetch the data sources with the DatabaseClient method

    # Confirm only all approved data sources are retrieved

    pytest.fail("Test not implemented")


def test_get_needs_identification_data_sources(live_database_client):
    # Add new data sources to the database, at least two labeled 'needs identification' and one not

    # Fetch the data sources with the DatabaseClient method

    # Confirm only all data sources labeled 'needs identification' are retrieved

    pytest.fail("Test not implemented")
