import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

from utilities.common import get_alembic_conn_string
from tests.alembic.AlembicRunner import AlembicRunner


@pytest.fixture()
def alembic_config():
    alembic_cfg = Config("alembic.ini")
    yield alembic_cfg


@pytest.fixture()
def db_engine():
    engine = create_engine(get_alembic_conn_string())
    yield engine
    engine.dispose()


@pytest.fixture()
def connection(db_engine):
    connection = db_engine.connect()
    yield connection
    connection.close()


@pytest.fixture()
def alembic_runner(connection, alembic_config) -> AlembicRunner:
    alembic_config.attributes["connection"] = connection
    alembic_config.set_main_option("sqlalchemy.url", get_alembic_conn_string())
    runner = AlembicRunner(
        alembic_config=alembic_config,
        inspector=inspect(connection),
        metadata=MetaData(),
        connection=connection,
        session=scoped_session(sessionmaker(bind=connection)),
    )
    try:
        runner.downgrade("base")
    except Exception:
        runner.reset_schema()
        runner.stamp("base")
    yield runner
    runner.upgrade("head")
    runner.session.close()
