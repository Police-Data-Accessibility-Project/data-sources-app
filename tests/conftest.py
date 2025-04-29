import logging
from collections import namedtuple
from unittest.mock import MagicMock

import dotenv
import pytest
from _pytest.monkeypatch import MonkeyPatch
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine

from config import limiter
from database_client.database_client import DatabaseClient
from tests.helper_scripts.common_mocks_and_patches import patch_and_return_mock
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import (
    TestDataCreatorDBClient,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from utilities.common import get_alembic_conn_string, downgrade_to_base

# Load environment variables
dotenv.load_dotenv()


@pytest.fixture
def dev_db_client() -> DatabaseClient:
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
    from app import create_app

    mock_db = mocker.MagicMock()
    monkeypatch.setattr("app.initialize_psycopg_connection", lambda: mock_db)
    app = create_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True
    with app.test_client() as client:
        yield ClientWithMockDB(client, mock_db)


@pytest.fixture()
def flask_client_with_db(monkeypatch):
    """
    Creates a client with database connection
    :return:
    """
    from app import create_app

    mock_get_flask_app_secret_key = MagicMock(return_value="test")
    monkeypatch.setattr(
        "app.get_flask_app_cookie_encryption_key", mock_get_flask_app_secret_key
    )
    app = create_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True
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
        lambda a, b, no_auth: access_info_mock,
    )
    return access_info_mock


@pytest.fixture
def mock_database_client(monkeypatch):
    mock = patch_and_return_mock(
        f"resources.PsycopgResource.DatabaseClient", monkeypatch
    )
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
def test_table_data(live_database_client: DatabaseClient):
    """
    Removes existing test table data and generates test data for the test table
    Generates test data for the test table
    :param dev_db_client:
    :return:
    """

    live_database_client.execute_raw_sql(
        """
    DELETE FROM test_table;
    """
    )

    live_database_client.execute_raw_sql(
        """
    INSERT INTO test_table (pet_name, species) VALUES 
    ('Arthur', 'Aardvark'),
    ('Jimbo', 'Cat'),
    ('Simon', 'Bear');
    """
    )


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
    monkeypatch.setattr(
        "middleware.flask_response_manager.make_response", mock.make_response
    )
    monkeypatch.setattr("middleware.flask_response_manager.abort", mock.abort)
    # Create a fake abort exception to use in tests
    mock.abort.side_effect = FakeAbort
    return mock


@pytest.fixture
def clear_data_requests(dev_db_client: DatabaseClient):
    """
    Clear `data_requests` and associated tables
    :param dev_db_client:
    :return:
    """
    dev_db_client.execute_raw_sql("DELETE FROM DATA_REQUESTS;")


@pytest.fixture(scope="session")
def test_data_creator_db_client() -> TestDataCreatorDBClient:
    yield TestDataCreatorDBClient()


@pytest.fixture(scope="function")
def test_data_creator_flask(monkeysession) -> TestDataCreatorFlask:
    from app import create_app

    mock_get_flask_app_secret_key = MagicMock(return_value="test")
    monkeysession.setattr(
        "app.get_flask_app_cookie_encryption_key", mock_get_flask_app_secret_key
    )
    mock_scheduler_manager = MagicMock()
    monkeysession.setattr("app.SchedulerManager", mock_scheduler_manager)
    app = create_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # Disable rate limiting for tests
    limiter.enabled = False
    with app.test_client() as client:
        tdc = TestDataCreatorFlask(client)
        tdc.clear_test_data()
        yield tdc
    limiter.enabled = True


@pytest.fixture(scope="session")
def monkeysession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    conn_string = get_alembic_conn_string()
    engine = create_engine(conn_string)
    # Base.metadata.drop_all(engine)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_section_option("logger_alembic", "level", "WARN")
    logging.getLogger("alembic").setLevel(logging.CRITICAL)
    logging.disable(logging.CRITICAL)
    alembic_cfg.attributes["connection"] = engine.connect()
    alembic_cfg.set_main_option("sqlalchemy.url", conn_string)
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        # Downgrade to base and try again
        downgrade_to_base(alembic_cfg, engine)
        connection = alembic_cfg.attributes["connection"]
        connection.exec_driver_sql("DROP SCHEMA public CASCADE;")
        connection.exec_driver_sql("CREATE SCHEMA public;")
        connection.commit()
        command.upgrade(alembic_cfg, "head")
    yield
    downgrade_to_base(alembic_cfg, engine)
    # Base.metadata.create_all(engine)
