"""This module contains pytest fixtures employed by middleware tests."""

from collections import namedtuple
from unittest.mock import MagicMock

import psycopg2
import pytest
from dotenv import load_dotenv
from psycopg2.extras import DictCursor

from app import create_app
from database_client.database_client import DatabaseClient
from middleware.util import get_env_variable
from tests.helper_scripts.helper_functions import insert_test_agencies_and_sources
from tests.helper_scripts.test_data_generator import TestDataGenerator


@pytest.fixture
def dev_db_connection() -> psycopg2.extensions.connection:
    """
    Create reversible connection to dev database.

    Sets up connection to development database
    and creates a session that is rolled back after the test completes
    to undo any operations performed during the test.
    :return:
    """
    load_dotenv()
    dev_db_connection_string = get_env_variable("DEV_DB_CONN_STRING")
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
def db_cursor(
    dev_db_connection: psycopg2.extensions.connection,
) -> psycopg2.extensions.cursor:
    """
    Create cursor for reversible database operations.

    Create a cursor to execute database operations, with savepoint management.
    This is to ensure that changes made during the test can be rolled back.
    """
    cur = dev_db_connection.cursor(cursor_factory=DictCursor)

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
    Insert test agencies and sources into test data.

    Will roll back in case of error.

    :param dev_db_connection:
    :return:
    """
    try:
        insert_test_agencies_and_sources(dev_db_connection.cursor())
    except psycopg2.errors.UniqueViolation:
        dev_db_connection.rollback()
    return dev_db_connection


ClientWithMockDB = namedtuple("ClientWithMockDB", ["client", "mock_db"])


@pytest.fixture
def client_with_mock_db(mocker, monkeypatch) -> ClientWithMockDB:
    """
    Create a client with a mocked database connection
    :param mocker:
    :return:
    """
    mock_db = mocker.MagicMock()
    monkeypatch.setattr("app.initialize_psycopg2_connection", lambda: mock_db)
    app = create_app()
    with app.test_client() as client:
        yield ClientWithMockDB(client, mock_db)


@pytest.fixture
def client_with_db(dev_db_connection: psycopg2.extensions.connection, monkeypatch):
    """
    Creates a client with database connection
    :param dev_db_connection:
    :return:
    """
    mock_get_flask_app_secret_key = MagicMock(return_value='test')
    monkeypatch.setattr("app.initialize_psycopg2_connection", lambda: dev_db_connection)
    monkeypatch.setattr("app.get_flask_app_secret_key", mock_get_flask_app_secret_key)
    app = create_app()
    with app.test_client() as client:
        yield client


@pytest.fixture
def bypass_api_required(monkeypatch):
    monkeypatch.setattr("middleware.security.validate_token", lambda: None)


@pytest.fixture
def live_database_client(db_cursor, test_client, session) -> DatabaseClient:
    """
    Returns a database client with a live connection to the database
    :param db_cursor:
    :return:
    """
    return DatabaseClient(db_cursor, test_client, session)

@pytest.fixture
def xylonslyvania_test_data(db_cursor):
    """
    Adds XylonsLyvania data to the database, then rolls back the transaction.
    """
    tcg = TestDataGenerator(db_cursor)
    tcg.build_savepoint("xylonslyvania_test_data")
    tcg.build_xylonslvania()
    yield
    tcg.rollback_savepoint()

