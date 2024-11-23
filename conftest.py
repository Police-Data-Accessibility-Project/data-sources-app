import os
from unittest.mock import MagicMock

import dotenv
import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy.orm import sessionmaker, scoped_session

# from middleware.models import db

from app import create_app
from config import limiter
from database_client.database_client import DatabaseClient
from middleware.util import get_env_variable
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import (
    TestDataCreatorDBClient,
)

# Load environment variables
dotenv.load_dotenv()

@pytest.fixture(scope="session")
def monkeysession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def test_data_creator_flask(monkeysession) -> TestDataCreatorFlask:
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
def test_data_creator_db_client() -> TestDataCreatorDBClient:
    yield TestDataCreatorDBClient()
