from datetime import datetime, timezone, timedelta

from werkzeug.exceptions import Conflict
from werkzeug.security import generate_password_hash

from db.client.core import DatabaseClient
from endpoints.instantiations.auth_.signup.dto import UserStandardSignupRequestDTO
from middleware.common_response_formatting import message_response
from middleware.primary_resource_logic.api_key import generate_token
from middleware.primary_resource_logic.user_queries import UserRequestDTO
from middleware.security.jwt.core import SimpleJWT
from middleware.security.jwt.enums import JWTPurpose
from middleware.third_party_interaction_logic.mailgun import send_via_mailgun
from middleware.util.url import create_web_app_url
from tests.helper_scripts.helper_functions_simple import add_query_params


def signup_wrapper(
    db_client: DatabaseClient,
    dto: UserStandardSignupRequestDTO,
):
    if db_client.get_user_id(email=dto.email) is not None:
        raise Conflict("User with email already exists.")

    if db_client.pending_user_exists(email=dto.email):
        raise Conflict(
            "User with email has already signed up. " +
            "Please validate your email or request a new validation email."
        )

    jwt_token = _setup_pending_user(db_client, dto)

    send_signup_link(
        email=dto.email,
        token=jwt_token.encode(),
    )

    return _validation_email_sent_response(email=dto.email)


def _get_signup_link(token: str):
    url = create_web_app_url("validate/email")
    url = add_query_params(url=url, params={"token": token})
    return url


def _get_signup_text(signup_link: str):
    return f"""
    Welcome to PDAP! If you meant to create an account, please verify your email by clicking this link. \n\n

    {signup_link}

    \n\nWe're happy to have you in our community. If you'd like, you can reply to this email with a bit more about what you hope to accomplish, or if there's any way we can support your project. You are also invited to join us in Discord, where you can chat with our team and other folks interested in police data: https://discord.gg/wMqex8nKZJ
    """


def _get_signup_html(signup_link: str):
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
    signup_link = _get_signup_link(token=token)

    text = _get_signup_text(signup_link=signup_link)

    html = _get_signup_html(signup_link=signup_link)

    send_via_mailgun(
        to_email=email,
        subject="Please validate your account",
        text=text,
        html=html,
        bcc="josh.chamberlain@pdap.io",
    )


def _validation_email_sent_response(email: str):
    return message_response(
        message=f"Validation email sent to {email}. " +
        f"To complete sign up, please validate your email.",
    )


def _get_validation_expiry() -> float:
    return (datetime.now(tz=timezone.utc) + timedelta(days=1)).timestamp()


def _setup_pending_user(db_client: DatabaseClient, dto: UserStandardSignupRequestDTO) -> SimpleJWT:
    """
    Sets up pending user with given information
    and returns the validation token wrapped in a JWT
    """
    token = generate_token()
    password_digest = generate_password_hash(dto.password)
    db_client.create_pending_user(
        email=dto.email,
        password_digest=password_digest,
        validation_token=token,
        capacities=dto.capacities,
    )
    jwt_token = get_validation_token_jwt(dto.email, token)
    return jwt_token


def get_validation_token_jwt(email: str, token: str):
    jwt_token = SimpleJWT(
        sub={
            "email": email,
            "token": token,
        },
        exp=_get_validation_expiry(),
        purpose=JWTPurpose.VALIDATE_EMAIL,
    )
    return jwt_token
