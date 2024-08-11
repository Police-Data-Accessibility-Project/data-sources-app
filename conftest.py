from unittest.mock import MagicMock

import dotenv
import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session

from middleware.models import db

from app import create_app


@pytest.fixture(scope="module")
def monkeymodule():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="module")
def test_client(monkeymodule):
    mock_get_flask_app_secret_key = MagicMock(return_value='test')
    monkeymodule.setattr("app.get_flask_app_secret_key", mock_get_flask_app_secret_key)

    app = create_app(testing=True)

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client


@pytest.fixture
def session() -> sqlalchemy.orm.scoping.scoped_session:
    connection = db.engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))

    # Overwrite the db.session with the scoped session
    db.session = session

    yield session

    session.close()
    transaction.rollback()
    connection.close()
