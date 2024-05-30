import json
import uuid
from urllib.parse import quote

import psycopg2
import pytest
from tests.fixtures import connection_with_test_data, dev_db_connection, client_with_db
from tests.helper_functions import (
    create_test_user_api,
    create_api_key,
    give_user_admin_role,
)


def test_data_sources_by_id_get(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)
    response = client_with_db.get(
        "/data-sources-by-id/SOURCE_UID_1",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200
    assert response.json["data"]["homepage_url"] == "http://src1.com"


def test_data_sources_by_id_put(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    user_info = create_test_user_api(client_with_db)
    give_user_admin_role(connection_with_test_data, user_info)
    api_key = create_api_key(client_with_db, user_info)
    desc = str(uuid.uuid4())
    response = client_with_db.put(
        f"/data-sources-by-id/SOURCE_UID_1",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"description": desc},
    )
    assert response.status_code == 200
    cursor = connection_with_test_data.cursor()
    cursor.execute(
        """
        SELECT description
        FROM data_sources
        WHERE airtable_uid = 'SOURCE_UID_1'
        """
    )
    result = cursor.fetchone()
    assert result[0] == desc
