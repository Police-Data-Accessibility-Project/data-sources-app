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

@patch(GET_ENV_PATCH_ROUTE)
@patch(CONNECT_PATCH_ROUTE)
def test_initialize_psycopg2_connection_success(mock_connect, mock_get_env_variable):
    mock_get_env_variable.return_value = "test_connection_url"
    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection

    connection = initialize_psycopg2_connection()

    assert connection == mock_connection
    mock_get_env_variable.assert_called_once_with("DO_DATABASE_URL")
    mock_connect.assert_called_once_with(
        "test_connection_url",
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
    )


@patch(GET_ENV_PATCH_ROUTE)
@patch(CONNECT_PATCH_ROUTE)
def test_initialize_psycopg2_connection_failure(mock_connect, mock_get_env_variable):
    mock_get_env_variable.return_value = "test_connection_url"
    mock_connect.side_effect = psycopg2.OperationalError("Connection failed")

    with pytest.raises(DatabaseInitializationError):
        initialize_psycopg2_connection()
    mock_get_env_variable.assert_called_once_with("DO_DATABASE_URL")
    mock_connect.assert_called_once_with(
        "test_connection_url",
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
    )
