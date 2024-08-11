import os

import dotenv
import pytest
from sqlalchemy.orm import sessionmaker, scoped_session

from middleware.models import db

from app import create_app


@pytest.fixture(scope="module")
def test_client():
    app = create_app(testing=True)

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
