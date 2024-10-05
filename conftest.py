import os
from unittest.mock import MagicMock

import dotenv
import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy.orm import sessionmaker, scoped_session

#from middleware.models import db

from app import create_app
from config import limiter
from middleware.util import get_env_variable
from tests.helper_scripts.common_test_data import TestDataCreator

# Load environment variables
dotenv.load_dotenv()


@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = get_env_variable(
        "DEV_DB_CONN_STRING"
    )  # Connect to pre-existing test database
    app.config["TESTING"] = True

    db.init_app(app)

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client



@pytest.fixture
def session():
    connection = db.engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))

    # Overwrite the db.session with the scoped session
    db.session = session

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def monkeysession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def test_data_creator_session_scope(monkeysession) -> TestDataCreator:
    mock_get_flask_app_secret_key = MagicMock(return_value="test")
    monkeysession.setattr(
        "app.get_flask_app_cookie_encryption_key", mock_get_flask_app_secret_key
    )
    app = create_app()
    # Disable rate limiting for tests
    limiter.enabled = False
    with app.test_client() as client:
        yield TestDataCreator(client)
    limiter.enabled = True
