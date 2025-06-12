import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession, sessionmaker, Session
from sqlalchemy.orm import sessionmaker

from db.exceptions import DatabaseInitializationError
from middleware.util.env import get_env_variable


def initialize_sqlalchemy_session() -> sessionmaker[Session]:
    """
    Initializes a connection to a PostgreSQL database using SQLAlchemy obtained from an environment variable.
    If the connection fails, it raises a DatabaseInitializationError.

    :return: A SQLAlchemy session object if successful.
    """
    try:
        do_database_url = get_env_variable("DO_DATABASE_URL")
        do_database_url = "postgresql+psycopg" + do_database_url[10:]

        engine = create_engine(do_database_url, pool_pre_ping=True)
        session = sessionmaker(bind=engine)
        return session

    except sqlalchemy.exc.SQLAlchemyError as e:
        raise DatabaseInitializationError(e) from e
