import psycopg2
import os
from psycopg2.extensions import connection as PgConnection
from typing import Union, Dict, List


def initialize_psycopg2_connection() -> (
    Union[PgConnection, Dict[str, Union[int, List]]]
):
    """
    Initializes a connection to a PostgreSQL database using psycopg2 with connection parameters
    obtained from an environment variable. If the connection fails, it returns a default dictionary
    indicating no data sources are available.

    The function sets keepalive parameters to maintain the connection active during periods of inactivity.

    :return: A psycopg2 connection object if successful, or a dictionary with a count of 0 and an empty data list upon failure.
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
