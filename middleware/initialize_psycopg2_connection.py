import psycopg2
import os
from typing import Union, Dict, Any
from psycopg2.extensions import connection

def initialize_psycopg2_connection() -> Union[connection, Dict[str, Any]]:
    """
    Initializes and returns a connection to a PostgreSQL database using psycopg2, based on the database URL obtained
    from an environment variable named "DO_DATABASE_URL". Implements TCP keepalive settings to maintain the connection.

    The function aims to establish a robust connection suitable for long-running applications, using environment-based
    configuration to enhance security and flexibility.

    If the connection cannot be established due to an error (e.g., misconfiguration, network issues), the function
    gracefully handles the exception by printing an error message and returning a standardized data structure with a
    count of 0 and an empty data list.

    Returns:
        psycopg2.extensions.connection: A connection object to the PostgreSQL database.
        Dict[str, Any]: A fallback dictionary with keys 'count' and 'data' in case of an error.
    """
    try:
        DO_DATABASE_URL = os.getenv("DO_DATABASE_URL")

        return psycopg2.connect(
            DO_DATABASE_URL,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
        )

    except:
        print("Error while initializing the DigitalOcean client with psycopg2.")
        data_sources = {"count": 0, "data": []}

        return data_sources
