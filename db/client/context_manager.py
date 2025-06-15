from contextlib import contextmanager

from db.client.core import DatabaseClient


@contextmanager
def setup_database_client() -> DatabaseClient:
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
