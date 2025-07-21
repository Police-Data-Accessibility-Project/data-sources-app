"""This module contains helper functions used by middleware pytests."""

from collections import namedtuple
from typing import Optional
from http import HTTPStatus

import sqlalchemy
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from db.client.core import DatabaseClient
from db.db_client_dataclasses import WhereMapping
from db.enums import ApprovalStatus, UserCapacityEnum
from middleware.enums import (
    PermissionsEnum,
    Relations,
    JurisdictionType,
    AgencyType,
)
from middleware.schema_and_dto.dtos.agencies.post import (
    AgencyInfoPostDTO,
    AgenciesPostDTO,
)
from endpoints.instantiations.auth_.routes import API_KEY_ROUTE
from tests.helpers.common_test_data import get_test_name, get_test_email
from tests.helpers.helper_classes.RequestValidator import RequestValidator
from tests.helpers.helper_classes.TestUserSetup import TestUserSetup
from tests.helpers.helper_classes.UserInfo import UserInfo
from tests.helpers.helper_functions_simple import get_authorization_header

TestTokenInsert = namedtuple("TestTokenInsert", ["id", "email", "token"])
TestUser = namedtuple("TestUser", ["id", "email", "password_hash"])


def create_test_user_db_client(db_client: DatabaseClient) -> UserInfo:
    email = get_test_email()
    password = get_test_name()
    password_digest = generate_password_hash(password)
    capacities = [UserCapacityEnum.POLICE, UserCapacityEnum.COMMUNITY_MEMBER]
    user_id = db_client.create_new_user(
        email=email,
        password_digest=password_digest,
        capacities=capacities,
    )
    return UserInfo(
        email=email, password=password, user_id=user_id, capacities=capacities
    )


JWTTokens = namedtuple("JWTTokens", ["access_token", "refresh_token"])


def login_and_return_jwt_tokens(client: FlaskClient, user_info: UserInfo) -> JWTTokens:
    """
    Login as a given user and return the associated session token,
    using the /login endpoint of the Flask API
    :param client:
    :param user_info:
    :return:
    """
    rv = RequestValidator(flask_client=client)
    data = rv.login(
        email=user_info.email,
        password=user_info.password,
    )
    return JWTTokens(
        access_token=data.get("access_token"),
        refresh_token=data.get("refresh_token"),
    )


def request_reset_password_api(client: FlaskClient, mocker, user_info):
    """
    Send a request to reset password via a Flask call to the /request-reset-password endpoint
    and return the reset token
    :param client:
    :param mocker:
    :param user_info:
    :return:
    """
    rv = RequestValidator(flask_client=client)
    return rv.request_reset_password(email=user_info.email, mocker=mocker)


def create_api_key(client_with_db: FlaskClient, jwt_authorization_header: dict) -> str:
    """
    Obtain an api key for the given user, via a Flask call to the /api-key endpoint
    :param client_with_db:
    :param user_info:
    :return: api_key
    """

    response = client_with_db.post(
        f"/auth{API_KEY_ROUTE}", headers=jwt_authorization_header
    )
    assert response.status_code == HTTPStatus.OK.value, (
        "API key creation not successful"
    )
    api_key = response.json.get("api_key")
    return api_key


def setup_get_typeahead_suggestion_test_data():
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

        agency_id = db_client.create_agency(
            dto=AgenciesPostDTO(
                agency_info=AgencyInfoPostDTO(
                    name="Xylodammerung Police Agency",
                    jurisdiction_type=JurisdictionType.STATE,
                    agency_type=AgencyType.POLICE,
                    approval_status=ApprovalStatus.APPROVED,
                ),
                location_ids=[location_id],
            )
        )
        db_client.execute_raw_sql("CALL refresh_typeahead_agencies();")
        db_client.execute_raw_sql("CALL refresh_typeahead_locations();")

        return agency_id

    except sqlalchemy.exc.IntegrityError:
        pass


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
    jwt_tokens = login_and_return_jwt_tokens(client, user_info)
    jwt_authorization_header = get_authorization_header(
        scheme="Bearer", token=jwt_tokens.access_token
    )
    api_key = create_api_key(client, jwt_authorization_header=jwt_authorization_header)
    return TestUserSetup(
        user_info,
        api_key,
        api_authorization_header=get_authorization_header(
            scheme="Basic", token=api_key
        ),
        jwt_authorization_header=jwt_authorization_header,
    )


def create_admin_test_user_setup(flask_client: FlaskClient) -> TestUserSetup:
    tus_admin = create_test_user_setup(
        flask_client,
        permissions=[
            PermissionsEnum.READ_ALL_USER_INFO,
            PermissionsEnum.DB_WRITE,
            PermissionsEnum.USER_CREATE_UPDATE,
            PermissionsEnum.ARCHIVE_WRITE,
            PermissionsEnum.GITHUB_SYNC,
            PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES,
        ],
    )
    return tus_admin
