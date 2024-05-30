import psycopg2
import pytest
from tests.fixtures import connection_with_test_data, dev_db_connection, client_with_db
from tests.helper_functions import create_test_user_api, create_api_key


def test_agencies_get(
    client_with_db, dev_db_connection: psycopg2.extensions.connection
):
    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)
    response = client_with_db.get(
        "/agencies/2",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200
    assert len(response.json["data"]) > 0

