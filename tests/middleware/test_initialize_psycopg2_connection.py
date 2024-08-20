import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from psycopg2.extensions import connection as PgConnection
from middleware.initialize_psycopg2_connection import (
    initialize_psycopg2_connection,
    DatabaseInitializationError,
)

PATCH_ROOT = "middleware.initialize_psycopg2_connection"
GET_ENV_PATCH_ROUTE = PATCH_ROOT + ".get_env_variable"
CONNECT_PATCH_ROUTE = PATCH_ROOT + ".psycopg2.connect"


def test_initialize_psycopg2_connection():
    """
    Test that initialize_psycopg2_connection returns a psycopg2 connection object.
    And that, if the connection is closed, it is reopened.
    :return:
    """
    conn = initialize_psycopg2_connection()

    assert isinstance(conn, PgConnection)
    assert conn.closed == 0

    conn.close()

    assert conn.closed == 1

    conn = initialize_psycopg2_connection()

    assert isinstance(conn, PgConnection)
    assert conn.closed == 0
