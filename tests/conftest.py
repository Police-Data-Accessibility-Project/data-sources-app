import datetime
import logging
from collections import namedtuple
from typing import Any, Generator
from unittest.mock import MagicMock

import dotenv
import pytest
from _pytest.monkeypatch import MonkeyPatch
from alembic import command
from alembic.config import Config
from psycopg import IntegrityError
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError as IntegrityErrorSA

from config import limiter
from db.client.core import DatabaseClient
from db.enums import LocationType
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.county import County
from db.models.implementations.core.location.locality import Locality
from db.models.implementations.core.location.us_state import USState
from db.models.implementations.core.record.type import RecordType
from middleware.enums import Relations, RecordTypesEnum
from tests.helpers.helper_classes.TestUserSetup import TestUserSetup
from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.wipe import wipe_database
from utilities.common import get_alembic_conn_string

# Load environment variables
dotenv.load_dotenv()


# TODO: Redundant with Live Database Client. Consolidate and remove this.
@pytest.fixture
def dev_db_client() -> Generator[DatabaseClient, Any, None]:
    db_client = DatabaseClient()
    yield db_client


ClientWithMockDB = namedtuple("ClientWithMockDB", ["client", "mock_db"])


@pytest.fixture
def client_with_mock_db(mocker, monkeypatch) -> Generator[ClientWithMockDB, Any, None]:
    """Create a client with a mocked database connection"""
    from app import create_flask_app

    mock_db = mocker.MagicMock()
    monkeypatch.setattr("app.initialize_psycopg_connection", lambda: mock_db)
    app = create_flask_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True
    with app.test_client() as client:
        yield ClientWithMockDB(client, mock_db)


@pytest.fixture()
def flask_client_with_db(monkeypatch):
    """Creates a client with database connection"""
    from app import create_flask_app

    mock_get_flask_app_secret_key = MagicMock(return_value="test")
    monkeypatch.setattr(
        "app.get_flask_app_cookie_encryption_key", mock_get_flask_app_secret_key
    )
    app = create_flask_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def bypass_jwt_required(monkeypatch):
    """A fixture to bypass the jwt required decorator for testing"""
    monkeypatch.setattr(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda a, b, c, d, e, f: None,
    )


@pytest.fixture
def live_database_client() -> Generator[DatabaseClient, Any, None]:
    """Returns a database client with a live connection to the database"""
    db_client = DatabaseClient()
    # Wipe database before returning
    wipe_database(db_client)

    yield db_client


@pytest.fixture
def test_table_data(live_database_client: DatabaseClient):
    """Removes existing test table data and generates test data for the test table."""

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


@pytest.fixture
def clear_data_requests(dev_db_client: DatabaseClient):
    """Clear `data_requests` and associated tables"""
    dev_db_client.execute_raw_sql("DELETE FROM DATA_REQUESTS;")


@pytest.fixture(scope="session")
def test_data_creator_db_client() -> Generator[TestDataCreatorDBClient, Any, None]:
    yield TestDataCreatorDBClient()


@pytest.fixture(scope="session")
def flask_client(monkeysession):
    from app import create_flask_app

    mock_get_flask_app_secret_key = MagicMock(return_value="test")
    monkeysession.setattr(
        "app.get_flask_app_cookie_encryption_key", mock_get_flask_app_secret_key
    )
    mock_scheduler_manager = MagicMock()
    monkeysession.setattr("app.SchedulerManager", mock_scheduler_manager)
    app = create_flask_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # Disable rate limiting for tests
    limiter.enabled = False
    with app.test_client() as client:
        yield client
    limiter.enabled = True


@pytest.fixture(scope="function")
def test_data_creator_flask(flask_client) -> TestDataCreatorFlask:
    tdc = TestDataCreatorFlask(flask_client)
    tdc.clear_test_data()
    yield tdc


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
    except Exception:
        # Downgrade to base and try again
        connection = alembic_cfg.attributes["connection"]
        connection.exec_driver_sql("DROP SCHEMA public CASCADE;")
        connection.exec_driver_sql("CREATE SCHEMA public;")
        connection.commit()
        command.upgrade(alembic_cfg, "head")
    yield
    connection = alembic_cfg.attributes["connection"]
    connection.exec_driver_sql("DROP SCHEMA public CASCADE;")
    connection.exec_driver_sql("CREATE SCHEMA public;")
    connection.commit()

    # Base.metadata.create_all(engine)


@pytest.fixture
def pennsylvania_id(live_database_client):
    query = (
        select(Location.id)
        .where(
            USState.state_name == "Pennsylvania",
            Location.type == LocationType.STATE.value,
        )
        .join(USState, Location.state_id == USState.id)
    )
    return live_database_client.scalar(query)


@pytest.fixture
def california_id(live_database_client):
    query = (
        select(Location.id)
        .where(USState.state_name == "California")
        .join(USState, Location.state_id == USState.id)
    )
    return live_database_client.scalar(query)


@pytest.fixture
def allegheny_id(live_database_client, pennsylvania_id) -> int:
    query = (
        select(Location.id)
        .where(
            County.name == "Allegheny",
        )
        .join(County, Location.county_id == County.id)
    )
    return live_database_client.scalar(query)


@pytest.fixture
def pittsburgh_id(live_database_client) -> int:
    query = select(County.id).where(County.name == "Allegheny")
    county_id = live_database_client.scalar(query)

    try:
        _ = live_database_client.create_locality(
            table_name=Relations.LOCALITIES.value,
            column_value_mappings={"county_id": county_id, "name": "Pittsburgh"},
        )
    except (IntegrityError, IntegrityErrorSA):
        pass

    query = (
        select(Location.id)
        .where(Locality.name == "Pittsburgh")
        .join(Locality, Location.locality_id == Locality.id)
    )
    return live_database_client.scalar(query)


@pytest.fixture
def national_id(live_database_client) -> int:
    query = select(Location.id).where(Location.type == LocationType.NATIONAL.value)
    return live_database_client.scalar(query)


@pytest.fixture(autouse=True)
def mock_send_via_mailgun(monkeypatch) -> Generator[MagicMock, Any, None]:
    paths = [
        "middleware.primary_resource_logic.contact",
        "middleware.webhook_logic",
        "middleware.primary_resource_logic.data_requests_.post",
        "middleware.primary_resource_logic.notifications.notifications",
        "endpoints.instantiations.auth_.signup.middleware",
    ]

    mock_send_via_mailgun = MagicMock()

    for path in paths:
        monkeypatch.setattr(f"{path}.send_via_mailgun", mock_send_via_mailgun)

    yield mock_send_via_mailgun


@pytest.fixture
def test_agencies(test_data_creator_db_client) -> list[int]:
    """Create test agencies and returns their IDs."""
    tdc = test_data_creator_db_client
    agency_ids = []
    for _ in range(5):
        agency_ids.append(tdc.agency().id)
    return agency_ids


@pytest.fixture
def sample_record_type_id(live_database_client) -> int:
    """Returns the ID of the OTHER record type."""
    query = select(RecordType.id).where(RecordType.name == RecordTypesEnum.OTHER.value)
    return live_database_client.scalar(query)


@pytest.fixture
def user_admin(test_data_creator_flask) -> TestUserSetup:
    return test_data_creator_flask.get_admin_tus()


@pytest.fixture
def user_standard(test_data_creator_flask) -> TestUserSetup:
    return test_data_creator_flask.standard_user()


@pytest.fixture
def tomorrow() -> datetime.date:
    return datetime.date.today() + datetime.timedelta(days=1)
