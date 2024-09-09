"""This module contains pytest fixtures employed by middleware tests."""

from collections import namedtuple
from importlib import reload
from types import ModuleType
from unittest import mock
from unittest.mock import MagicMock

import psycopg
import pytest
from dotenv import load_dotenv
from psycopg.rows import namedtuple_row

from app import create_app
from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from middleware.util import get_env_variable
from tests.helper_scripts.helper_functions import (
    insert_test_agencies_and_sources,
    create_test_user_setup,
)
from tests.helper_scripts.helper_classes.IntegrationTestSetup import IntegrationTestSetup
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.test_data_generator import TestDataGenerator


@pytest.fixture
def dev_db_connection() -> psycopg.Connection:
    """
    Create reversible connection to dev database.

    Sets up connection to development database
    and creates a session that is rolled back after the test completes
    to undo any operations performed during the test.
    :return:
    """
    load_dotenv()
    dev_db_connection_string = get_env_variable("DEV_DB_CONN_STRING")
    connection = psycopg.connect(
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
    dev_db_connection: psycopg.Connection,
) -> psycopg.Cursor:
    """
    Create cursor for reversible database operations.

    Create a cursor to execute database operations, with savepoint management.
    This is to ensure that changes made during the test can be rolled back.
    """
    cur = dev_db_connection.cursor(row_factory=namedtuple_row)

    # Start a savepoint
    cur.execute("SAVEPOINT test_savepoint")

    yield cur

    # Rollback to the savepoint to ignore commits within the test
    cur.execute("ROLLBACK TO SAVEPOINT test_savepoint")
    cur.close()


@pytest.fixture
def dev_db_client() -> DatabaseClient:
    db_client = DatabaseClient()
    yield db_client


@pytest.fixture
def connection_with_test_data(
) -> psycopg.Connection:
    """
    Insert test agencies and sources into test data.

    Will roll back in case of error.

    :param dev_db_connection:
    :return:
    """
    db_client = DatabaseClient()
    try:
        insert_test_agencies_and_sources(db_client.connection.cursor())
    except psycopg.errors.UniqueViolation:
        db_client.connection.rollback()
    return db_client.connection


@pytest.fixture
def db_client_with_test_data(
    connection_with_test_data: psycopg.Connection,
) -> DatabaseClient:
    db_client = DatabaseClient()
    yield db_client


ClientWithMockDB = namedtuple("ClientWithMockDB", ["client", "mock_db"])


@pytest.fixture
def client_with_mock_db(mocker, monkeypatch) -> ClientWithMockDB:
    """
    Create a client with a mocked database connection
    :param mocker:
    :return:
    """
    mock_db = mocker.MagicMock()
    monkeypatch.setattr("app.initialize_psycopg_connection", lambda: mock_db)
    app = create_app()
    with app.test_client() as client:
        yield ClientWithMockDB(client, mock_db)


@pytest.fixture
def flask_client_with_db(monkeypatch):
    """
    Creates a client with database connection
    :param dev_db_connection:
    :return:
    """
    mock_get_flask_app_secret_key = MagicMock(return_value="test")
    monkeypatch.setattr(
        "app.get_flask_app_cookie_encryption_key", mock_get_flask_app_secret_key
    )
    app = create_app()
    with app.test_client() as client:
        yield client


# region Bypass Decorators


def patch_decorator(monkeypatch, module: ModuleType):
    # Patch the decorator where it is being imported from
    monkeypatch.setattr("app.decorators.func_decor", lambda x: x)

    # Reload the uut module to apply the patched decorator
    reload(module)

    # Add a finalizer to stop all patches and reload the original module
    yield  # This yield statement allows the test to run

    mock.patch.stopall()
    reload(module)  # Reload to restore the original decorator


@pytest.fixture
def bypass_api_key_required(monkeypatch):
    """
    A fixture to bypass the api_key required decorator for testing
    :param monkeypatch:
    :return:
    """
    monkeypatch.setattr("middleware.decorators.check_api_key", lambda: None)


@pytest.fixture
def bypass_permissions_required(monkeypatch):
    """
    A fixture to bypass the permissions required decorator for testing
    :param monkeypatch:
    :return:
    """
    monkeypatch.setattr("middleware.decorators.check_permissions", lambda x: None)


@pytest.fixture
def bypass_jwt_required(monkeypatch):
    """
    A fixture to bypass the jwt required decorator for testing
    :param monkeypatch:
    :return:
    """
    monkeypatch.setattr(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda a, b, c, d, e, f: None,
    )


@pytest.fixture
def bypass_authentication_required(monkeypatch):
    """
    A fixture to bypass the authentication required decorator for testing
    :param monkeypatch:
    :return:
    """
    monkeypatch.setattr(
        "middleware.decorators.get_authentication",
        lambda a, b: None,
    )


# endregion


@pytest.fixture
def live_database_client() -> DatabaseClient:
    """
    Returns a database client with a live connection to the database
    :param db_cursor:
    :return:
    """
    db_client = DatabaseClient()
    yield db_client


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


@pytest.fixture
def test_user_admin(flask_client_with_db) -> TestUserSetup:
    """
    Creates a test user with admin permissions
    :param flask_client_with_db:
    :return:
    """

    db_client = DatabaseClient()

    tus_admin = create_test_user_setup(flask_client_with_db)
    db_client.add_user_permission(
        tus_admin.user_info.email, PermissionsEnum.READ_ALL_USER_INFO
    )
    db_client.add_user_permission(tus_admin.user_info.email, PermissionsEnum.DB_WRITE)
    return tus_admin


@pytest.fixture
def integration_test_admin_setup(flask_client_with_db) -> IntegrationTestSetup:
    db_client = DatabaseClient()
    tus_admin = create_test_user_setup(flask_client_with_db)
    db_client.add_user_permission(
        tus_admin.user_info.email, PermissionsEnum.READ_ALL_USER_INFO
    )
    db_client.add_user_permission(tus_admin.user_info.email, PermissionsEnum.DB_WRITE)
    return IntegrationTestSetup(
        flask_client=flask_client_with_db, db_client=db_client, tus=tus_admin
    )


@pytest.fixture
def test_table_data(live_database_client: DatabaseClient):
    """
    Removes existing test table data and generates test data for the test table
    Generates test data for the test table
    :param dev_db_client:
    :return:
    """

    live_database_client.execute_raw_sql("""
    DELETE FROM test_table;
    """)

    live_database_client.execute_raw_sql("""
    INSERT INTO test_table (pet_name, species) VALUES 
    ('Arthur', 'Aardvark'),
    ('Jimbo', 'Cat'),
    ('Simon', 'Bear');
    """)

class FakeAbort(Exception):
    pass

@pytest.fixture
def mock_flask_response_manager(monkeypatch):
    """
    Mock the flask-native functions embedded within the FlaskResponseManager
    :param monkeypatch:
    :return:
    """
    mock = MagicMock()
    monkeypatch.setattr("middleware.flask_response_manager.make_response", mock.make_response)
    monkeypatch.setattr("middleware.flask_response_manager.abort", mock.abort)
    # Create a fake abort exception to use in tests
    mock.abort.side_effect = FakeAbort
    return mock