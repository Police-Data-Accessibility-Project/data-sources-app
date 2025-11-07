from http import HTTPStatus
from typing import Any

import sqlalchemy
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from db.client.core import DatabaseClient
from db.exceptions import DatabaseInitializationError
from db.queries.builder.core import QueryBuilderBase
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

        engine = create_engine(
            do_database_url,
            poolclass=NullPool,
        )
        sm = sessionmaker(bind=engine)
        return sm

    except sqlalchemy.exc.SQLAlchemyError as e:
        raise DatabaseInitializationError(e) from e

def run_query_builder(
    query_builder: QueryBuilderBase
) -> Any:
    try:
        db_client = DatabaseClient()
        return db_client.run_query_builder(query_builder)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e)
        )