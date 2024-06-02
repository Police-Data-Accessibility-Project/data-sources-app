"""This module contains helper functions used by middleware pytests."""

import uuid
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Optional

import psycopg2.extensions
from flask.testing import FlaskClient

TestTokenInsert = namedtuple("TestTokenInsert", ["id", "email", "token"])
TestUser = namedtuple("TestUser", ["id", "email", "password_hash"])


def insert_test_agencies_and_sources(cursor: psycopg2.extensions.cursor) -> None:
    """
    Insert test agencies and sources into database.

    :param cursor:
    :return:
    """
    cursor.execute(
        """
        INSERT INTO
        PUBLIC.DATA_SOURCES (
            airtable_uid,
            NAME,
            DESCRIPTION,
            RECORD_TYPE,
            SOURCE_URL,
            APPROVAL_STATUS,
            URL_STATUS
        )
        VALUES
        ('SOURCE_UID_1','Source 1','Description of src1',
            'Type A','http://src1.com','approved','available'),
        ('SOURCE_UID_2','Source 2','Description of src2',
            'Type B','http://src2.com','needs identification','available'),
        ('SOURCE_UID_3','Source 3', 'Description of src3',
            'Type C', 'http://src3.com', 'pending', 'available');

        INSERT INTO public.agencies
        (airtable_uid, name, municipality, state_iso,
            county_name, count_data_sources, lat, lng)
        VALUES 
            ('Agency_UID_1', 'Agency A', 'City A',
                'CA', 'County X', 3, 30, 20),
            ('Agency_UID_2', 'Agency B', 'City B',
                'NY', 'County Y', 2, 40, 50),
            ('Agency_UID_3', 'Agency C', 'City C',
                'TX', 'County Z', 1, 90, 60);

        INSERT INTO public.agency_source_link
        (airtable_uid, agency_described_linked_uid)
        VALUES
            ('SOURCE_UID_1', 'Agency_UID_1'),
            ('SOURCE_UID_2', 'Agency_UID_2'),
            ('SOURCE_UID_3', 'Agency_UID_3');
        """
    )


def get_reset_tokens_for_email(
    db_cursor: psycopg2.extensions.cursor, reset_token_insert: TestTokenInsert
) -> tuple:
    """
    Get all reset tokens associated with an email.

    :param db_cursor:
    :param reset_token_insert:
    :return:
    """
    db_cursor.execute(
        """
        SELECT email from RESET_TOKENS where email = %s
        """,
        (reset_token_insert.email,),
    )
    results = db_cursor.fetchall()
    return results


def create_reset_token(cursor: psycopg2.extensions.cursor) -> TestTokenInsert:
    """
    Create a test user and associated reset token.

    :param cursor:
    :return:
    """
    user = create_test_user(cursor)
    token = uuid.uuid4().hex
    cursor.execute(
        """
        INSERT INTO reset_tokens(email, token)
        VALUES (%s, %s)
        RETURNING id
        """,
        (user.email, token),
    )
    id = cursor.fetchone()[0]
    return TestTokenInsert(id=id, email=user.email, token=token)


def create_test_user(
    cursor,
    email="",
    password_hash="hashed_password_here",
    api_key="api_key_here",
    role=None,
) -> TestUser:
    """
    Create test user and return the id of the test user.

    :param cursor:
    :return: user id
    """
    if email == "":
        email = uuid.uuid4().hex + "@test.com"
    cursor.execute(
        """
        INSERT INTO users (email, password_digest, api_key, role)
        VALUES
        (%s, %s, %s, %s)
        RETURNING id;
        """,
        (email, password_hash, api_key, role),
    )
    return TestUser(
        id=cursor.fetchone()[0],
        email=email,
        password_hash=password_hash,
    )


QuickSearchQueryLogResult = namedtuple(
    "QuickSearchQueryLogResult", ["result_count", "updated_at"]
)


def get_most_recent_quick_search_query_log(
    cursor: psycopg2.extensions.cursor, search: str, location: str
) -> Optional[QuickSearchQueryLogResult]:
    """
    Retrieve most recent quick search query log for a search and location.

    :param cursor: The Cursor object of the database connection.
    :param search: The search query string.
    :param location: The location string.
    :return: A QuickSearchQueryLogResult object
        containing the result count and updated timestamp.
    """
    cursor.execute(
        """
        SELECT RESULT_COUNT, DATETIME_OF_REQUEST FROM QUICK_SEARCH_QUERY_LOGS WHERE
        search = %s AND location = %s ORDER BY DATETIME_OF_REQUEST DESC LIMIT 1
        """,
        (search, location),
    )
    result = cursor.fetchone()
    if result is None:
        return result
    return QuickSearchQueryLogResult(result_count=result[0], updated_at=result[1])


def has_expected_keys(result_keys: list, expected_keys: list) -> bool:
    """
    Check that given result includes expected keys.

    :param result:
    :param expected_keys:
    :return: True if has expected keys, false otherwise
    """
    return not set(expected_keys).difference(result_keys)


def get_boolean_dictionary(keys: tuple) -> dict:
    """
    Creates dictionary of booleans, all set to false.

    :param keys:
    :return: dictionary of booleans
    """
    d = {}
    for key in keys:
        d[key] = False
    return d


UserInfo = namedtuple("UserInfo", ["email", "password"])


def create_test_user_api(client: FlaskClient) -> UserInfo:
    """
    Create a test user through calling the /user endpoint via the Flask API
    :param client:
    :return:
    """
    email = str(uuid.uuid4())
    password = str(uuid.uuid4())
    response = client.post(
        "/user",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, "User creation not successful"
    return UserInfo(email=email, password=password)


def login_and_return_session_token(
    client_with_db: FlaskClient, user_info: UserInfo
) -> str:
    """
    Login as a given user and return the associated session token,
    using the /login endpoint of the Flask API
    :param client_with_db:
    :param user_info:
    :return:
    """
    response = client_with_db.post(
        "/login",
        json={"email": user_info.email, "password": user_info.password},
    )
    assert response.status_code == 200, "User login unsuccessful"
    session_token = response.json.get("data")
    return session_token


def get_user_password_digest(cursor: psycopg2.extensions.cursor, user_info):
    """
    Get the associated password digest of a user (given their email) from the database
    :param cursor:
    :param user_info:
    :return:
    """
    cursor.execute(
        """
        SELECT password_digest from users where email = %s
    """,
        (user_info.email,),
    )
    return cursor.fetchone()[0]


def request_reset_password_api(client_with_db, mocker, user_info):
    """
    Send a request to reset password via a Flask call to the /request-reset-password endpoint
    and return the reset token
    :param client_with_db:
    :param mocker:
    :param user_info:
    :return:
    """
    mocker.patch("resources.RequestResetPassword.requests.post")
    response = client_with_db.post(
        "/request-reset-password", json={"email": user_info.email}
    )
    token = response.json.get("token")
    return token


def create_api_key(client_with_db, user_info):
    """
    Obtain an api key for the given user, via a Flask call to the /api-key endpoint
    :param client_with_db:
    :param user_info:
    :return:
    """
    response = client_with_db.get(
        "/api_key", json={"email": user_info.email, "password": user_info.password}
    )
    assert response.status_code == 200, "API key creation not successful"
    api_key = response.json.get("api_key")
    return api_key


def insert_test_data_source(cursor: psycopg2.extensions.cursor) -> str:
    """
    Insert test data source and return id
    :param cursor:
    :return: randomly generated uuid
    """
    test_uid = str(uuid.uuid4())
    cursor.execute(
        """
        INSERT INTO
        PUBLIC.DATA_SOURCES (
            airtable_uid,
            NAME,
            DESCRIPTION,
            RECORD_TYPE,
            SOURCE_URL,
            APPROVAL_STATUS,
            URL_STATUS
        )
        VALUES
        (%s,'Example Data Source', 'Example Description',
            'Type A','http://src1.com','approved','available')
        """,
        (test_uid,),
    )
    return test_uid


def give_user_admin_role(
    connection: psycopg2.extensions.connection, user_info: UserInfo
):
    """
    Give the given user an admin role.
    :param connection:
    :param user_info:
    :return:
    """
    cursor = connection.cursor()

    cursor.execute(
        """
    UPDATE users
    SET role = 'admin'
    WHERE email = %s
    """,
        (user_info.email,),
    )

def check_response_status(response, status_code):
    assert response.status_code == status_code, f"Expected status code {status_code}, got {response.status_code}: {response.text}"