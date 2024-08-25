from contextlib import contextmanager
from http import HTTPStatus
import functools
from typing import Callable, Any, Union, Tuple, Dict

import psycopg
from flask_restx import abort, Resource

from config import config
from database_client.database_client import DatabaseClient
from middleware.initialize_psycopg_connection import initialize_psycopg_connection


def handle_exceptions(
    func: Callable[..., Any]
) -> Callable[..., Union[Any, Tuple[Dict[str, str], int]]]:
    """
    A decorator to handle exceptions raised by a function.

    :param func: The function to be decorated.
    :return: The decorated function.

    The decorated function handles any exceptions raised
    by the original function. If an exception occurs, the
    decorator performs a rollback on the psycopg connection,
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
        - kwargs (dict): Keyword arguments containing 'psycopg_connection' for database connection.
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
            config.connection = initialize_psycopg_connection()
        return config.connection

    @contextmanager
    def setup_database_client(self) -> DatabaseClient:
        """
        A context manager to setup a database client.

        Yields:
        - The database client.
        """
        db_client = DatabaseClient()
        try:
            yield db_client
        except Exception as e:
            raise e
