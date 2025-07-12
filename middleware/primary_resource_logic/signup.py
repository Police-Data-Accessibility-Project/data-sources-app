from werkzeug.exceptions import BadRequest

from db.client.core import DatabaseClient
from endpoints.instantiations.auth_.signup.middleware import send_signup_link, validation_email_sent_response, \
    get_validation_token_jwt
from middleware.primary_resource_logic.api_key import generate_token
from middleware.primary_resource_logic.login_queries import (
    access_and_refresh_token_response,
)
from middleware.schema_and_dto.dtos.signup import EmailOnlyDTO
from middleware.security.access_info.validate_email import ValidateEmailTokenAccessInfo


def validate_email_wrapper(
    db_client: DatabaseClient, access_info: ValidateEmailTokenAccessInfo
):
    pending_user_info = db_client.get_pending_user_with_token(
        validation_token=access_info.validate_email_token
    )
    if pending_user_info is None:
        raise BadRequest("Invalid validation token.")

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


def resend_validation_email_wrapper(
    db_client: DatabaseClient,
    dto: EmailOnlyDTO,
):
    email = dto.email
    if not db_client.pending_user_exists(email=email):
        raise BadRequest("Email provided not associated with any pending user.")

    token = generate_token()
    db_client.update_pending_user_validation_token(email=email, validation_token=token)
    jwt_token = get_validation_token_jwt(email, token)

    send_signup_link(
        email=email,
        token=jwt_token.encode(),
    )

    return validation_email_sent_response(email=email)
