from contextlib import contextmanager
from http import HTTPStatus
import functools
from typing import Callable, Any, Union, Tuple, Dict

import psycopg2
from flask_restx import abort, Resource
from psycopg2.extras import DictCursor
from sqlalchemy.orm import sessionmaker, scoped_session

from config import config
from database_client.database_client import DatabaseClient
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
from middleware.models import db

def handle_exceptions(
    func: Callable[..., Any]
) -> Callable[..., Union[Any, Tuple[Dict[str, str], int]]]:
    """
    A decorator to handle exceptions raised by a function.

    :param func: The function to be decorated.
    :return: The decorated function.

    The decorated function handles any exceptions raised
    by the original function. If an exception occurs, the
    decorator performs a rollback on the psycopg2 connection,
    prints the error message, and returns a dictionary with
    the error message and an HTTP status code of 500.

    Example usage:
    ```
    @handle_exceptions
    def my_function():
        # code goes here
    ```
    """

    @functools.wraps(func)
    def wrapper(
        self, *args: Any, **kwargs: Any
    ) -> Union[Any, Tuple[Dict[str, str], int]]:
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.get_connection().rollback()
            print(str(e))
            abort(
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value, message=str(e)
            )

    return wrapper


class PsycopgResource(Resource):
    def __init__(self, *args, **kwargs):
        """
        Initializes the resource with a database connection.
        - kwargs (dict): Keyword arguments containing 'psycopg2_connection' for database connection.
        """
        super().__init__(*args, **kwargs)

    def connection_is_closed(self) -> bool:
        """
        Per https://www.psycopg.org/docs/connection.html#connection.closed
        a connection is open is the integer attribute is 0,
        closed or broken of the integer attribute is nonzero

        A connection is only determined to be closed after
        an operation has been tried and failed.
        Thus, in the case of a closed connection, the operation will fail
        on the first run, then succeed on the second run.
        :return:
        """
        return config.connection.closed != 0

    def get_connection(self):
        if self.connection_is_closed():
            config.connection = initialize_psycopg2_connection()
        return config.connection

    def get_db_session(self):
        connection = db.engine.connect()
        transaction = connection.begin()
        session = scoped_session(sessionmaker(bind=connection))

        # Overwrite the db.session with the scoped session
        db.session = session
        
        try:
            yield session
        except Exception as e:
            transaction.rollback()
            raise e
        finally:
            session.close()
            connection.close()


    @contextmanager
    def setup_database_client(self) -> DatabaseClient:
        """
        A context manager to setup a database client.

        Yields:
        - The database client.
        """
        conn = self.get_connection()
        session = self.get_db_session()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                yield DatabaseClient(cursor, session)
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.commit()
