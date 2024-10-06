from collections import namedtuple
from importlib import reload
from types import ModuleType
from unittest import mock
from unittest.mock import MagicMock

import psycopg
import pytest

from app import create_app
from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from middleware.util import get_env_variable
from tests.helper_scripts.common_mocks_and_patches import patch_and_return_mock
from tests.helper_scripts.helper_classes.IntegrationTestSetup import IntegrationTestSetup
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions import insert_test_agencies_and_sources, create_test_user_setup



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


@pytest.fixture()
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
    access_info_mock = MagicMock()
    monkeypatch.setattr(
        "middleware.decorators.get_authentication",
        lambda a, b: access_info_mock,
    )
    return access_info_mock


@pytest.fixture
def mock_database_client(monkeypatch):
    mock = patch_and_return_mock(f"resources.PsycopgResource.DatabaseClient", monkeypatch)
    mock.return_value = MagicMock()
    return mock.return_value


@pytest.fixture
def live_database_client() -> DatabaseClient:
    """
    Returns a database client with a live connection to the database
    :return:
    """
    db_client = DatabaseClient()
    yield db_client


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

