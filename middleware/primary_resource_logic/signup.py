from datetime import datetime, timezone, timedelta
from http import HTTPStatus

from werkzeug.security import generate_password_hash

from database_client.database_client import DatabaseClient
from middleware.SimpleJWT import SimpleJWT, JWTPurpose
from middleware.access_logic import ValidateEmailTokenAccessInfo
from middleware.common_response_formatting import message_response
from middleware.primary_resource_logic.api_key import generate_token
from middleware.primary_resource_logic.login_queries import (
    access_and_refresh_token_response,
)
from middleware.primary_resource_logic.user_queries import UserRequestDTO
from middleware.schema_and_dto_logic.common_schemas_and_dtos import EmailOnlyDTO
from middleware.third_party_interaction_logic.mailgun_logic import send_via_mailgun
from middleware.util import create_web_app_url
from tests.helper_scripts.helper_functions_simple import add_query_params


def get_signup_link(token: str):
    url = create_web_app_url("validate/email")
    url = add_query_params(url=url, params={"token": token})
    return url


def get_signup_text(signup_link: str):
    return f"""
    Welcome to PDAP! If you meant to create an account, please verify your email by clicking this link. \n\n

    {signup_link}

    \n\nWe're happy to have you in our community. If you'd like, you can reply to this email with a bit more about what you hope to accomplish, or if there's any way we can support your project. You are also invited to join us in Discord, where you can chat with our team and other folks interested in police data: https://discord.gg/wMqex8nKZJ
    """


def get_signup_html(signup_link: str):
    return f"""
    <!DOCTYPE html>
    <head>
    <title>PDAP</title>
    </head>
    <body>
    <p> Welcome to PDAP! If you meant to create an account, <a href='{signup_link}'>please verify your email by clicking this link.</a> </p>
    
    <p> We're happy to have you in our community. 
    If you'd like, you can reply to this email with a bit more about 
    what you hope to accomplish, or if there's any way we can support your 
    project. You are also invited to <a href='https://discord.gg/wMqex8nKZJ'>join us in Discord</a>, where you can 
    chat with our team and other folks interested in police data.</p>
    </body>
    </html>
    """


def send_signup_link(email: str, token: str):

    signup_link = get_signup_link(token=token)

    text = get_signup_text(signup_link=signup_link)

    html = get_signup_html(signup_link=signup_link)

    send_via_mailgun(
        to_email=email,
        subject="Please validate your account",
        text=text,
        html=html,
        bcc="josh.chamberlain@pdap.io",
    )


def validation_email_sent_response(email: str):
    return message_response(
        message=f"Validation email sent to {email}. To complete sign up, please validate your email.",
    )


def get_validation_expiry() -> float:
    return (datetime.now(tz=timezone.utc) + timedelta(days=1)).timestamp()


def signup_wrapper(
    db_client: DatabaseClient,
    dto: UserRequestDTO,
):
    if db_client.get_user_id(email=dto.email) is not None:
        return message_response(
            status_code=HTTPStatus.CONFLICT,
            message=f"User with email already exists.",
        )

    if db_client.pending_user_exists(email=dto.email):
        return message_response(
            status_code=HTTPStatus.CONFLICT,
            message=f"User with email has already signed up. "
            f"Please validate your email or request a new validation email.",
        )

    jwt_token = setup_pending_user(db_client, dto)

    send_signup_link(
        email=dto.email,
        token=jwt_token.encode(),
    )

    return validation_email_sent_response(email=dto.email)


def validate_email_wrapper(
    db_client: DatabaseClient, access_info: ValidateEmailTokenAccessInfo
):

    pending_user_info = db_client.get_pending_user_with_token(
        validation_token=access_info.validate_email_token
    )
    if pending_user_info is None:
        return message_response(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Invalid validation token.",
        )
    email = pending_user_info["email"]
    db_client.create_new_user(
        email=email,
        password_digest=pending_user_info["password_digest"],
    )
    db_client.delete_pending_user(
        email=email,
    )

    return access_and_refresh_token_response(
        email=email,
        message="Successfully validated email and logged in.",
    )


def setup_pending_user(db_client: DatabaseClient, dto: UserRequestDTO) -> SimpleJWT:
    """
    Sets up pending user with given information
    and returns the validation token wrapped in a JWT
    """
    token = generate_token()
    password_digest = generate_password_hash(dto.password)
    db_client.create_pending_user(
        email=dto.email, password_digest=password_digest, validation_token=token
    )
    jwt_token = get_validation_token_jwt(dto.email, token)
    return jwt_token


def get_validation_token_jwt(email: str, token):
    jwt_token = SimpleJWT(
        sub={
            "email": email,
            "token": token,
        },
        exp=get_validation_expiry(),
        purpose=JWTPurpose.VALIDATE_EMAIL,
    )
    return jwt_token


def resend_validation_email_wrapper(
    db_client: DatabaseClient,
    dto: EmailOnlyDTO,
):

    email = dto.email
    if not db_client.pending_user_exists(email=email):
        return message_response(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Email provided not associated with any pending user.",
        )

    token = generate_token()
    db_client.update_pending_user_validation_token(email=email, validation_token=token)
    jwt_token = get_validation_token_jwt(email, token)

    send_signup_link(
        email=email,
        token=jwt_token.encode(),
    )

    return validation_email_sent_response(email=email)
