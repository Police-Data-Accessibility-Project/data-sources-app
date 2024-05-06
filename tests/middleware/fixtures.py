import os

import psycopg2
import pytest
from dotenv import load_dotenv

from tests.middleware.helper_functions import insert_test_agencies_and_sources


@pytest.fixture
def dev_db_connection() -> psycopg2.extensions.cursor:
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


@pytest.fixture
def db_cursor(dev_db_connection: psycopg2.extensions.connection) -> psycopg2.extensions.cursor:
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


@pytest.fixture
def connection_with_test_data(
    dev_db_connection: psycopg2.extensions.connection,
) -> psycopg2.extensions.connection:
    """
    Insert test agencies and sources into test data, rolling back in case of error
    :param dev_db_connection:
    :return:
    """
    try:
        insert_test_agencies_and_sources(dev_db_connection.cursor())
    except psycopg2.errors.UniqueViolation:
        dev_db_connection.rollback()
    return dev_db_connection
