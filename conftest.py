import os
from unittest.mock import MagicMock

import dotenv
import pytest
from _pytest.monkeypatch import MonkeyPatch
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from config import limiter
from middleware.util import get_env_variable
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import (
    TestDataCreatorDBClient,
)

# Load environment variables
dotenv.load_dotenv()


def get_alembic_conn_string() -> str:
    conn_string = get_env_variable("DO_DATABASE_URL")
    conn_string = conn_string.replace("postgresql", "postgresql+psycopg")
    return conn_string


def downgrade_to_base(alembic_cfg: Config, engine):
    try:
        command.downgrade(alembic_cfg, "base")
    except Exception as e:
        with engine.connect() as connection:
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
            connection.commit()

        command.stamp(alembic_cfg, "base")
        raise e


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    conn_string = get_alembic_conn_string()
    engine = create_engine(conn_string)
    # Base.metadata.drop_all(engine)
    alembic_cfg = Config("alembic.ini")
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


@pytest.fixture(scope="session")
def monkeysession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="function")
def test_data_creator_flask(setup_database, monkeysession) -> TestDataCreatorFlask:
    from app import create_app

    mock_get_flask_app_secret_key = MagicMock(return_value="test")
    monkeysession.setattr(
        "app.get_flask_app_cookie_encryption_key", mock_get_flask_app_secret_key
    )
    app = create_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True
    # Disable rate limiting for tests
    limiter.enabled = False
    with app.test_client() as client:
        yield TestDataCreatorFlask(client)
    limiter.enabled = True


@pytest.fixture(scope="session")
def test_data_creator_db_client(setup_database) -> TestDataCreatorDBClient:
    yield TestDataCreatorDBClient()
