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
from werkzeug.security import generate_password_hash

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
from tests.helper_scripts.common_test_data import get_test_name, get_test_email
from tests.helper_scripts.constants import TEST_RESPONSE
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_classes.UserInfo import UserInfo

TestTokenInsert = namedtuple("TestTokenInsert", ["id", "email", "token"])
TestUser = namedtuple("TestUser", ["id", "email", "password_hash"])


def check_is_test_response(response):
    check_response_status(response, TEST_RESPONSE.status_code)
    assert response.json == TEST_RESPONSE.response


def create_test_user_db_client(db_client: DatabaseClient) -> UserInfo:
    email = get_test_email()
    password = get_test_name()
    password_digest = generate_password_hash(password)
    user_id = db_client.create_new_user(email=email, password_digest=password_digest)
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


def get_authorization_header(
    scheme: str,
    token: str,
) -> dict:
    return {"Authorization": f"{scheme} {token}"}


def create_test_user_setup(
    client: FlaskClient, permissions: Optional[list[PermissionsEnum]] = None
) -> TestUserSetup:
    db_client = DatabaseClient()
    user_info = create_test_user_db_client(db_client)
    if permissions is None:
        permissions = []
    elif not isinstance(permissions, list):
        permissions = [permissions]
    for permission in permissions:
        db_client.add_user_permission(user_id=user_info.user_id, permission=permission)
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
    tus_admin = create_test_user_setup(
        flask_client,
        permissions=[PermissionsEnum.READ_ALL_USER_INFO, PermissionsEnum.DB_WRITE],
    )
    return tus_admin


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
