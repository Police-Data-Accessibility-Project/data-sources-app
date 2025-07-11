from psycopg import Connection as PgConnection
from db.helpers_.psycopg import (
    initialize_psycopg_connection,
)

PATCH_ROOT = "middleware.initialize_psycopg_connection"
GET_ENV_PATCH_ROUTE = PATCH_ROOT + ".get_env_variable"
CONNECT_PATCH_ROUTE = PATCH_ROOT + ".psycopg.connect"


def test_initialize_psycopg_connection():
    """
    Test that initialize_psycopg_connection returns a psycopg connection object.
    And that, if the connection is closed, it is reopened.
    :return:
    """
    conn = initialize_psycopg_connection()
    assert isinstance(conn, PgConnection)
    assert conn.closed == 0

    conn.close()

    assert conn.closed == 1

    conn = initialize_psycopg_connection()

    assert isinstance(conn, PgConnection)
    assert conn.closed == 0
