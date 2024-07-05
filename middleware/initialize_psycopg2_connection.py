import psycopg2
from psycopg2.extensions import connection as PgConnection
from middleware.util import get_env_variable


class DatabaseInitializationError(Exception):
    """
    Custom Exception to be raised when psycopg2 connection initialization fails.
    """

    def __init__(self, message="Failed to initialize psycopg2 connection."):
        self.message = message
        super().__init__(self.message)


def initialize_psycopg2_connection() -> PgConnection:
    """
    Initializes a connection to a PostgreSQL database using psycopg2 with connection parameters
    obtained from an environment variable. If the connection fails, it returns a default dictionary
    indicating no data sources are available.

    The function sets keepalive parameters to maintain the connection active during periods of inactivity.

    :return: A psycopg2 connection object if successful, or a dictionary with a count of 0 and an empty data list upon failure.
    """
    try:
        DO_DATABASE_URL = get_env_variable("DO_DATABASE_URL")

        return psycopg2.connect(
            DO_DATABASE_URL,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
        )

    except psycopg2.OperationalError as e:
        raise DatabaseInitializationError(e) from e
