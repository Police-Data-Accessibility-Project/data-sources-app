"""This module contains helper functions used by middleware pytests."""

import uuid
from collections import namedtuple
from typing import Optional
from http import HTTPStatus
from unittest.mock import MagicMock
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import psycopg
from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient
from middleware.custom_dataclasses import (
    GithubUserInfo,
    OAuthCallbackInfo,
    FlaskSessionCallbackInfo,
)
from middleware.enums import CallbackFunctionsEnum, PermissionsEnum
from resources.ApiKey import API_KEY_ROUTE
from tests.helper_scripts.common_test_data import TEST_RESPONSE
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_classes.UserInfo import UserInfo

TestTokenInsert = namedtuple("TestTokenInsert", ["id", "email", "token"])
TestUser = namedtuple("TestUser", ["id", "email", "password_hash"])


def insert_test_agencies_and_sources(cursor: psycopg.Cursor) -> None:
    """
    Insert test agencies and sources into database.

    :param cursor:
    :return:
    """

    DatabaseClient().execute_raw_sql(
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


def insert_test_agencies_and_sources_if_not_exist(cursor: psycopg.Cursor):
    try:
        insert_test_agencies_and_sources(cursor)
    except psycopg.errors.UniqueViolation:  # Data already inserted
        pass


def get_reset_tokens_for_email(
    db_cursor: psycopg.Cursor, reset_token_insert: TestTokenInsert
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


def create_reset_token(cursor: psycopg.Cursor) -> TestTokenInsert:
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


def check_is_test_response(response):
    check_response_status(response, TEST_RESPONSE.status_code)
    assert response.json == TEST_RESPONSE.response


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
    "QuickSearchQueryLogResult", ["result_count", "updated_at", "results"]
)


def get_most_recent_quick_search_query_log(
    cursor: psycopg.Cursor, search: str, location: str
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
        SELECT RESULT_COUNT, CREATED_AT, RESULTS FROM QUICK_SEARCH_QUERY_LOGS WHERE
        search = %s AND location = %s ORDER BY CREATED_AT DESC LIMIT 1
        """,
        (search, location),
    )
    result = cursor.fetchone()
    if result is None:
        return result
    return QuickSearchQueryLogResult(
        result_count=result[0], updated_at=result[1], results=result[2]
    )


def get_boolean_dictionary(keys: tuple) -> dict[str, bool]:
    """
    Creates dictionary of booleans, all set to false.

    :param keys:
    :return: dictionary of booleans
    """
    d = {}
    for key in keys:
        d[key] = False
    return d


def search_with_boolean_dictionary(
    data: list[dict],
    boolean_dictionary: dict[str, bool],
    key_to_search_on: str,
):
    """
    Search data with boolean dictionary.
    Updates boolean dictionary with found data.

    :param data:
    :param boolean_dictionary:
    :param key_to_search_on:
    """
    for result in data:
        name = result[key_to_search_on]
        if name in boolean_dictionary:
            boolean_dictionary[name] = True


def create_test_user_api(client: FlaskClient) -> UserInfo:
    """
    Create a test user through calling the /user endpoint via the Flask API
    :param client:
    :return:
    """
    email = str(uuid.uuid4())
    password = str(uuid.uuid4())
    response = client.post(
        "user",
        json={"email": email, "password": password},
    )
    user_id = DatabaseClient().get_user_id(email)
    check_response_status(response, HTTPStatus.OK.value)
    return UserInfo(email=email, password=password, user_id=user_id)


JWTTokens = namedtuple("JWTTokens", ["access_token", "refresh_token"])


def login_and_return_jwt_tokens(
    client_with_db: FlaskClient, user_info: UserInfo
) -> JWTTokens:
    """
    Login as a given user and return the associated session token,
    using the /login endpoint of the Flask API
    :param client_with_db:
    :param user_info:
    :return:
    """
    response = client_with_db.post(
        "/api/login",
        json={"email": user_info.email, "password": user_info.password},
    )
    assert response.status_code == HTTPStatus.OK.value, "User login unsuccessful"
    return JWTTokens(
        access_token=response.json.get("access_token"),
        refresh_token=response.json.get("refresh_token"),
    )


def get_user_password_digest(cursor: psycopg.Cursor, user_info):
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
    mocker.patch(
        "middleware.primary_resource_logic.reset_token_queries.send_password_reset_link"
    )
    response = client_with_db.post(
        "/api/request-reset-password", json={"email": user_info.email}
    )
    token = response.json.get("token")
    return token


def create_api_key(client_with_db, user_info) -> str:
    """
    Obtain an api key for the given user, via a Flask call to the /api-key endpoint
    :param client_with_db:
    :param user_info:
    :return: api_key
    """
    response = client_with_db.post(
        f"/auth{API_KEY_ROUTE}",
        json={"email": user_info.email, "password": user_info.password},
    )
    assert (
        response.status_code == HTTPStatus.OK.value
    ), "API key creation not successful"
    api_key = response.json.get("api_key")
    return api_key


def create_api_key_db(cursor, user_id: str):
    api_key = uuid.uuid4().hex
    cursor.execute("UPDATE users SET api_key = %s WHERE id = %s", (api_key, user_id))
    return api_key


def insert_test_data_source(db_client: DatabaseClient) -> str:
    """
    Insert test data source and return id
    :param cursor:
    :return: randomly generated uuid
    """
    test_uid = str(uuid.uuid4())
    db_client.execute_raw_sql(
        query="""
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
        vars=(test_uid,),
    )
    return test_uid


def give_user_admin_role(connection: psycopg.Connection, user_info: UserInfo):
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


def setup_get_typeahead_suggestion_test_data(cursor: psycopg.Cursor):
    try:
        cursor.execute("SAVEPOINT typeahead_suggestion_test_savepoint")

        # State (via state_names table)
        cursor.execute(
            "insert into state_names (state_iso, state_name) values ('XY', 'Xylonsylvania')"
        )
        # County (via counties table)
        cursor.execute(
            "insert into counties(fips, name, state_iso) values ('12345', 'Arxylodon', 'XY')"
        )

        # Locality (via agencies table)
        cursor.execute(
            """insert into agencies 
            (name, airtable_uid, municipality, state_iso, county_fips, county_name, jurisdiction_type) 
            values 
            ('Xylodammerung Police Agency', 'XY_SOURCE_UID', 'Xylodammerung', 'XY', '12345', 'Arxylodon', 'state')"""
        )

        # Refresh materialized view
        cursor.execute("CALL refresh_typeahead_agencies();")
        cursor.execute("CALL refresh_typeahead_locations();")
    except psycopg.errors.UniqueViolation:
        cursor.execute("ROLLBACK TO SAVEPOINT typeahead_suggestion_test_savepoint")


def patch_post_callback_functions(
    monkeypatch,
    github_user_info: GithubUserInfo,
    callback_functions_enum: CallbackFunctionsEnum,
    callback_params: dict,
):
    mock_get_oauth_callback_info = MagicMock(
        return_value=OAuthCallbackInfo(github_user_info)
    )
    mock_get_flask_session_callback_info = MagicMock(
        return_value=FlaskSessionCallbackInfo(
            callback_functions_enum=callback_functions_enum,
            callback_params=callback_params,
        )
    )
    monkeypatch.setattr(
        "middleware.callback_primary_logic.get_oauth_callback_info",
        mock_get_oauth_callback_info,
    )
    monkeypatch.setattr(
        "middleware.callback_primary_logic.get_flask_session_callback_info",
        mock_get_flask_session_callback_info,
    )


def patch_setup_callback_session(
    monkeypatch,
    resources_module_name: str,
) -> MagicMock:
    mock_setup_callback_session = MagicMock()
    monkeypatch.setattr(
        f"resources.{resources_module_name}.setup_callback_session",
        mock_setup_callback_session,
    )
    return mock_setup_callback_session


def create_fake_github_user_info(email: Optional[str] = None) -> GithubUserInfo:
    return GithubUserInfo(
        user_id=uuid.uuid4().hex,
        user_email=uuid.uuid4().hex if email is None else email,
    )


def create_test_user_setup(
    client: FlaskClient, permissions: Optional[list[PermissionsEnum]] = None
) -> TestUserSetup:
    user_info = create_test_user_api(client)
    db_client = DatabaseClient()
    if permissions is None:
        permissions = []
    elif not isinstance(permissions, list):
        permissions = [permissions]
    for permission in permissions:
        db_client.add_user_permission(user_email=user_info.email, permission=permission)
    api_key = create_api_key(client, user_info)
    jwt_tokens = login_and_return_jwt_tokens(client, user_info)
    return TestUserSetup(
        user_info,
        api_key,
        api_authorization_header={"Authorization": f"Basic {api_key}"},
        jwt_authorization_header={"Authorization": f"Bearer {jwt_tokens.access_token}"},
    )


def create_test_user_setup_db_client(
    db_client: DatabaseClient, permissions: Optional[list[PermissionsEnum]] = None
) -> TestUserSetup:
    if permissions is None:
        permissions = []
    elif not isinstance(permissions, list):
        permissions = [permissions]
    email = uuid.uuid4().hex
    password_digest = uuid.uuid4().hex
    user_id = db_client.add_new_user(email, password_digest)
    api_key = db_client.get_user_info(email).api_key
    for permission in permissions:
        db_client.add_user_permission(email, permission)
    return TestUserSetup(
        UserInfo(email, password_digest, user_id),
        api_key,
        {"Authorization": f"Basic {api_key}"},
    )


def create_test_user_db_client(db_client: DatabaseClient) -> UserInfo:
    email = uuid.uuid4().hex
    password_digest = uuid.uuid4().hex
    user_id = db_client.add_new_user(email, password_digest)
    return UserInfo(email, password_digest, user_id)


def add_query_params(url, params: dict):
    """
    Add query parameters to a URL.
    :param url:
    :param params:
    :return:
    """

    # Parse the original URL into components
    url_parts = list(urlparse(url))

    # Extract existing query parameters (if any) and update with the new ones
    query = dict(parse_qs(url_parts[4]))
    query.update(params)

    # Encode the updated query parameters
    url_parts[4] = urlencode(query, doseq=True)

    # Rebuild the URL with the updated query parameters
    return urlunparse(url_parts)
