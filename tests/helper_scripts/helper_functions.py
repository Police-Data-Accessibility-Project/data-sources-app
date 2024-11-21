"""This module contains helper functions used by middleware pytests."""

import uuid
from collections import namedtuple
from datetime import datetime, timezone, timedelta
from typing import Optional
from http import HTTPStatus
from unittest.mock import MagicMock
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import psycopg
import sqlalchemy
from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from middleware.custom_dataclasses import (
    GithubUserInfo,
    OAuthCallbackInfo,
    FlaskSessionCallbackInfo,
)
from middleware.enums import (
    CallbackFunctionsEnum,
    PermissionsEnum,
    Relations,
    JurisdictionType,
)
from resources.ApiKeyResource import API_KEY_ROUTE
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.constants import TEST_RESPONSE
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
    db_client = DatabaseClient()
    location_id_1 = db_client._select_from_relation(
        relation_name=Relations.LOCATIONS_EXPANDED.value,
        columns=["id"],
        where_mappings=WhereMapping.from_dict(
            {
                "locality_name": "New Rochelle",
                "state_iso": "NY",
                "county_name": "Westchester",
            }
        ),
    )[0]["id"]

    location_id_2 = db_client._select_from_relation(
        relation_name=Relations.LOCATIONS_EXPANDED.value,
        columns=["id"],
        where_mappings=WhereMapping.from_dict(
            {
                "locality_name": "Saint Peters",
                "state_iso": "MO",
                "county_name": "St. Charles",
            }
        ),
    )[0]["id"]

    location_id_3 = db_client._select_from_relation(
        relation_name=Relations.LOCATIONS_EXPANDED.value,
        columns=["id"],
        where_mappings=WhereMapping.from_dict(
            {
                "locality_name": "Folly Beach",
                "state_iso": "SC",
                "county_name": "Charleston",
            }
        ),
    )[0]["id"]

    DatabaseClient().execute_raw_sql(
        """
        INSERT INTO
        PUBLIC.DATA_SOURCES (
            NAME,
            SUBMITTED_NAME,
            DESCRIPTION,
            SOURCE_URL,
            APPROVAL_STATUS,
            URL_STATUS
        )
        VALUES
        ('Source 1', 'Source 1','Description of src1',
            'http://src1.com','approved','available'),
        ('Source 2', 'Source 2','Description of src2',
            'http://src2.com','needs identification','available'),
        ('Source 3', 'Source 3','Description of src3',
            'http://src3.com', 'pending', 'available');
        """
    )
    db_client.execute_raw_sql(
        """
        INSERT INTO public.agencies
        (airtable_uid, name, submitted_name, location_id, lat, lng, jurisdiction_type)
        VALUES 
            ('Agency_UID_1', 'Agency A', 'Agency A', %s, 30, 20, 'state'),
            ('Agency_UID_2', 'Agency B', 'Agency B', %s, 40, 50, 'state'),
            ('Agency_UID_3', 'Agency C', 'Agency C', %s, 90, 60, 'state');
    """,
        vars=(location_id_1, location_id_2, location_id_3),
    )

    db_client.execute_raw_sql(
        """
        INSERT INTO public.link_agencies_data_sources
        (data_source_uid, agency_uid)
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
        email = get_test_name()
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
    email = get_test_name()
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


def get_user_password_digest(user_info):
    """
    Get the associated password digest of a user (given their email) from the database
    :param user_info:
    :return:
    """
    return DatabaseClient().execute_raw_sql(
        """
        SELECT password_digest from users where email = %s
    """,
        (user_info.email,),
    )[0]


def request_reset_password_api(client_with_db, mocker, user_info):
    """
    Send a request to reset password via a Flask call to the /request-reset-password endpoint
    and return the reset token
    :param client_with_db:
    :param mocker:
    :param user_info:
    :return:
    """
    mock = mocker.patch(
        "middleware.primary_resource_logic.reset_token_queries.send_password_reset_link"
    )
    response = client_with_db.post(
        "/api/request-reset-password", json={"email": user_info.email}
    )
    return mock.call_args[1]["token"]


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
            SOURCE_URL,
            APPROVAL_STATUS,
            URL_STATUS
        )
        VALUES
        (%s,'Example Data Source', 'Example Description',
            'http://src1.com','approved','available')
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


def setup_get_typeahead_suggestion_test_data(cursor: Optional[psycopg.Cursor] = None):
    db_client = DatabaseClient()
    try:

        state_id = db_client.create_or_get(
            table_name=Relations.US_STATES.value,
            column_value_mappings={"state_iso": "XY", "state_name": "Xylonsylvania"},
            column_to_return="id",
        )

        county_id = db_client.create_or_get(
            table_name=Relations.COUNTIES.value,
            column_value_mappings={
                "fips": "12345",
                "name": "Arxylodon",
                "state_iso": "XY",
                "state_id": state_id,
            },
            column_to_return="id",
        )

        locality_id = db_client.create_or_get(
            table_name=Relations.LOCALITIES.value,
            column_value_mappings={"name": "Xylodammerung", "county_id": county_id},
            column_to_return="id",
        )

        location_id = db_client._select_from_relation(
            relation_name=Relations.LOCATIONS.value,
            columns=["id"],
            where_mappings=WhereMapping.from_dict(
                {
                    "locality_id": locality_id,
                    "county_id": county_id,
                    "state_id": state_id,
                }
            ),
        )[0]["id"]

        agency_id = db_client.create_or_get(
            table_name=Relations.AGENCIES.value,
            column_value_mappings={
                "submitted_name": "Xylodammerung Police Agency",
                "jurisdiction_type": JurisdictionType.STATE,
                "location_id": location_id,
            },
            column_to_return="id",
        )

        db_client.execute_raw_sql("CALL refresh_typeahead_agencies();")
        db_client.execute_raw_sql("CALL refresh_typeahead_locations();")

        return agency_id

    except sqlalchemy.exc.IntegrityError:
        pass


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
    PATCH_ROOT = "middleware.primary_resource_logic.callback_primary_logic"
    monkeypatch.setattr(
        f"{PATCH_ROOT}.get_oauth_callback_info",
        mock_get_oauth_callback_info,
    )
    monkeypatch.setattr(
        f"{PATCH_ROOT}.get_flask_session_callback_info",
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
        user_email=get_test_name() if email is None else email,
    )


def get_authorization_header(
    scheme: str,
    token: str,
) -> dict:
    return {"Authorization": f"{scheme} {token}"}


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
        api_authorization_header=get_authorization_header(
            scheme="Basic", token=api_key
        ),
        jwt_authorization_header=get_authorization_header(
            scheme="Bearer", token=jwt_tokens.access_token
        ),
    )


def create_admin_test_user_setup(flask_client: FlaskClient) -> TestUserSetup:
    db_client = DatabaseClient()
    tus_admin = create_test_user_setup(
        flask_client,
        permissions=[PermissionsEnum.READ_ALL_USER_INFO, PermissionsEnum.DB_WRITE],
    )
    return tus_admin


def create_test_user_setup_db_client(
    db_client: DatabaseClient, permissions: Optional[list[PermissionsEnum]] = None
) -> TestUserSetup:
    if permissions is None:
        permissions = []
    elif not isinstance(permissions, list):
        permissions = [permissions]
    email = get_test_name()
    password_digest = uuid.uuid4().hex
    user_id = db_client.create_new_user(email, password_digest)
    api_key = db_client.get_user_info(email).api_key
    for permission in permissions:
        db_client.add_user_permission(email, permission)
    return TestUserSetup(
        UserInfo(email, password_digest, user_id),
        api_key,
        {"Authorization": f"Basic {api_key}"},
    )


def create_test_user_db_client(db_client: DatabaseClient) -> UserInfo:
    email = get_test_name()
    password_digest = get_test_name()
    user_id = db_client.create_new_user(email, password_digest)
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


def get_notification_valid_date():
    return datetime.now(timezone.utc) - timedelta(days=30)
