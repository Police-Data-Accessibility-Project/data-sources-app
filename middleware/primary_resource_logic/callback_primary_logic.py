from datetime import datetime, timezone, timedelta

from flask import Response, redirect

import jwt
from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.SimpleJWT import SimpleJWT, JWTPurpose
from middleware.common_response_formatting import message_response
from middleware.exceptions import UserNotFoundError
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.login_queries import (
    unauthorized_response,
    login_response,
)
from middleware.third_party_interaction_logic.callback_flask_sessions_logic import (
    get_callback_params,
    get_callback_function,
)
from middleware.custom_dataclasses import (
    FlaskSessionCallbackInfo,
)
from middleware.third_party_interaction_logic.callback_oauth_logic import (
    get_github_oauth_access_token,
)
from tests.helper_scripts.helper_functions import add_query_params


def get_flask_session_callback_info() -> FlaskSessionCallbackInfo:
    """
    Returns a FlaskSessionCallbackInfo object with the callback function and parameters
    :return:
    """
    return FlaskSessionCallbackInfo(
        callback_functions_enum=get_callback_function(),
        callback_params=get_callback_params(),
    )


def callback_outer_wrapper(db_client: DatabaseClient) -> Response:
    """
    Outer wrapper for the callback function.
    This wrapper interfaces with the functions which interface with the Flask Sessions and OAuth2 logic
    and passes the results into the callback_inner_wrapper
    :param db_client:
    :return:
    """
    gh_access_token = get_github_oauth_access_token()
    exp = (datetime.now(tz=timezone.utc) + timedelta(minutes=5)).timestamp()
    simple_jwt = SimpleJWT(
        sub=gh_access_token['access_token'],
        exp=exp,
        purpose=JWTPurpose.GITHUB_ACCESS_TOKEN
    )

    flask_session_callback_info = get_flask_session_callback_info()
    redirect_base_url = flask_session_callback_info.callback_params["redirect_url"]
    redirect_url = add_query_params(
        url=redirect_base_url,
        params={"gh_access_token": simple_jwt.encode()},
    )
    return redirect(
        location=redirect_url
    )





def user_exists(db_client: DatabaseClient, email: str) -> bool:
    try:
        db_client.get_user_info(email=email)
        return True
    except UserNotFoundError:
        return False

