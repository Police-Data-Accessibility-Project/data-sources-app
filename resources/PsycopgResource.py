from contextlib import contextmanager
from http import HTTPStatus
import functools
from typing import Callable, Any, Union, Tuple, Dict

from flask_restx import abort, Resource

from database_client.database_client import DatabaseClient


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
            self.psycopg2_connection.rollback()
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
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @contextmanager
    def setup_database_client(self) -> DatabaseClient:
        """
        A context manager to setup a database client.

        Yields:
        - The database client.
        """
        with self.psycopg2_connection.cursor() as cursor:
            try:
                yield DatabaseClient(cursor)
            except Exception as e:
                self.psycopg2_connection.rollback()
                raise e
            finally:
                self.psycopg2_connection.commit()
