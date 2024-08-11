"""Integration tests for /refresh-session endpoint."""

from http import HTTPStatus
import psycopg2.extensions

from tests.fixtures import dev_db_connection, flask_client_with_db
from tests.helper_scripts.helper_functions import create_test_user_api, login_and_return_api_key

# NOTE: Deprecated: rebuild later when setting up JWT tokens
# def test_refresh_session_post(
#     client_with_db, dev_db_connection: psycopg2.extensions.connection
# ):
#     """
#     Test that POST call to /refresh-session endpoint successfully generates a new session token, ensures the new token is different from the old one, and verifies the old token is removed while the new token exists in the session tokens table
#     """
#
#     test_user = create_test_user_api(client_with_db)
#     old_session_token = login_and_return_api_key(client_with_db, test_user)
#     response = client_with_db.post(
#         "/api/refresh-session", json={"session_token": old_session_token}
#     )
#     assert response.status_code == HTTPStatus.OK.value
#     new_session_token = response.json.get("data")
#
#     assert (
#         old_session_token != new_session_token
#     ), "New and old tokens should be different"
#
#     # Check that old_session_token is not in session tokens, and new_session token does
#     cursor = dev_db_connection.cursor()
#     cursor.execute(
#         """
#     SELECT * FROM session_tokens where token = %s;
#     """,
#         (new_session_token,),
#     )
#     rows = cursor.fetchall()
#     assert (
#         len(rows) == 1
#     ), "Only one row should exist for the session token in the session_tokens table"
#
#     cursor.execute(
#         """
#     SELECT * FROM session_tokens where token = %s;
#     """,
#         (old_session_token,),
#     )
#     rows = cursor.fetchall()
#     assert (
#         len(rows) == 0
#     ), "No row should exist for the old session token in the session_tokens table"
