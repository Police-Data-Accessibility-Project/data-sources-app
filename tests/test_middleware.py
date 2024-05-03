"""
This module runs pytests on functions interacting directly with the database -- the middleware
"""

import os
import uuid
from unittest.mock import patch

import psycopg2
import pytest
from dotenv import load_dotenv

from middleware.archives_queries import archives_get_results
from middleware.data_source_queries import (
    get_approved_data_sources,
    needs_identification_data_sources,
    data_source_by_id_results,
)
from middleware.login_queries import (
    login_results,
    create_session_token,
    token_results,
    is_admin,
)
from middleware.quick_search_query import unaltered_search_query, quick_search_query
from middleware.reset_token_queries import (
    check_reset_token,
    add_reset_token,
    delete_reset_token,
)
from middleware.user_queries import user_post_results, user_check_email
from tests.helper_test_middleware import (
    get_reset_tokens_for_email,
    create_reset_token,
    create_test_user,
    insert_test_agencies_and_sources,
)


@pytest.fixture()
def dev_db_connection():
    """
    Sets up connection to development database
    and creates a session that is rolled back after the test completes
    to undo any operations performed during the test.
    :return:
    """
    load_dotenv()
    dev_db_connection_string = os.getenv("DEV_DB_CONN_STRING")
    connection = psycopg2.connect(
        dev_db_connection_string,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
    )
    connection.autocommit = False

    yield connection

    # Rollback any changes made during the tests
    connection.rollback()

    connection.close()


@pytest.fixture()
def db_cursor(dev_db_connection):
    """
    Create a cursor to execute database operations, with savepoint management.
    This is to ensure that changes made during the test can be rolled back.
    """
    cur = dev_db_connection.cursor()

    # Start a savepoint
    cur.execute("SAVEPOINT test_savepoint")

    yield cur

    # Rollback to the savepoint to ignore commits within the test
    cur.execute("ROLLBACK TO SAVEPOINT test_savepoint")
    cur.close()


def test_unaltered_search_query(db_cursor):
    # TODO: Modify
    response = unaltered_search_query(db_cursor, "calls", "chicago")

    assert response


def test_data_sources(dev_db_connection):
    # TODO: Modify
    response = get_approved_data_sources(conn=dev_db_connection)

    assert response


def test_needs_identification(dev_db_connection):
    # TODO: Modify
    response = needs_identification_data_sources(conn=dev_db_connection)

    assert response


def test_data_sources_approved(dev_db_connection):
    # TODO: Adjust this test to insert approved and unapproved data sources prior.
    #       Ensure the results returned are only approved.
    response = get_approved_data_sources(conn=dev_db_connection)

    assert (
        len([d for d in response if "https://joinstatepolice.ny.gov/15-mile-run" in d])
        == 0
    )


def test_data_source_by_id_results(dev_db_connection):
    # TODO: Modify; insert data sources with specific id, ensure those are the ONLY data sources returned
    # Insert other data sources as well with different id
    response = data_source_by_id_results(
        data_source_id="rec00T2YLS2jU7Tbn", conn=dev_db_connection
    )

    assert response


def test_user_post_query(db_cursor):
    user_post_results(db_cursor, "unit_test", "unit_test")

    db_cursor.execute(f"SELECT email FROM users WHERE email = 'unit_test'")
    email_check = db_cursor.fetchone()[0]

    assert email_check == "unit_test"


def test_login_query(db_cursor):
    test_user = create_test_user(db_cursor)

    user_data = login_results(db_cursor, "example@example.com")

    assert user_data["password_digest"] == test_user.password_hash


def test_create_session_token_results(db_cursor):
    test_user = create_test_user(db_cursor)
    with patch("os.getenv", return_value="mysecretkey") as mock_getenv:
        token = create_session_token(db_cursor, test_user.id, test_user.email)
    new_token = token_results(db_cursor, token)

    assert new_token["email"] == test_user.email


def test_is_admin(db_cursor):
    """
    Creates and inserts two users, one an admin and the other not
    And then checks to see if the `is_admin` properly
    identifies both
    :param db_cursor:
    """
    regular_user = create_test_user(db_cursor)
    admin_user = create_test_user(
        cursor=db_cursor, email="admin@admin.com", role="admin"
    )
    assert is_admin(db_cursor, admin_user.email)
    assert not is_admin(db_cursor, regular_user.email)


def test_user_check_email(db_cursor):
    user = create_test_user(db_cursor)
    user_data = user_check_email(db_cursor, user.email)
    assert user_data["id"] == user.id


def test_check_reset_token(db_cursor):
    """
    Checks if a token existing in the database
    is properly returned by check_reset_token
    :param db_cursor:
    :return:
    """
    test_token_insert = create_reset_token(db_cursor)

    user_data = check_reset_token(db_cursor, test_token_insert.token)
    assert test_token_insert.id == user_data["id"]


def test_add_reset_token(db_cursor):
    """
    Checks if add_reset_token properly inserts a token
    for the given email in the database
    """
    user = create_test_user(db_cursor)
    token = uuid.uuid4().hex
    add_reset_token(db_cursor, user.email, token)
    db_cursor.execute(
        """
        SELECT id, token FROM RESET_TOKENS where email = %s
        """,
        (user.email,),
    )
    results = db_cursor.fetchall()
    assert len(results) == 1
    assert results[0][1] == token


def test_delete_reset_token(db_cursor):
    """
    Checks if token previously inserted is deleted
    by the delete_reset_token method
    """
    reset_token_insert = create_reset_token(db_cursor)
    results = get_reset_tokens_for_email(db_cursor, reset_token_insert)
    assert len(results) == 1
    delete_reset_token(db_cursor, reset_token_insert.email, reset_token_insert.token)
    results = get_reset_tokens_for_email(db_cursor, reset_token_insert)
    assert len(results) == 0


def test_archives_get_results(dev_db_connection, db_cursor):
    """
    Checks if archives_get_results picks up an added valid datasource
    """
    original_results = archives_get_results(dev_db_connection)
    db_cursor.execute(
        """
        INSERT INTO data_sources(airtable_uid, source_url, name, update_frequency, url_status) 
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            "fake_uid",
            "https://www.fake_source_url.com",
            "fake_name",
            "Annually",
            "unbroken",
        ),
    )
    new_results = archives_get_results(dev_db_connection)
    assert len(new_results) == len(original_results) + 1


def test_quicksearch_columns(dev_db_connection):
    try:
        insert_test_agencies_and_sources(dev_db_connection.cursor())
    except psycopg2.errors.UniqueViolation:
        dev_db_connection.rollback()
    # TODO: Something about the quick_search_query might be mucking up the savepoints. Address once you fix quick_search's logic issues
    results = quick_search_query(
        search="Source 1", location="City A", conn=dev_db_connection
    )
    # "Source 3" was listed as pending and shouldn't show up
    assert len(results['data']) == 1
    results = quick_search_query(
        search="Source 3", location="City C", conn=dev_db_connection
    )
    assert len(results['data']) == 0

    # Test that query inserted into log
