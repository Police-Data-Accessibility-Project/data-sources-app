from werkzeug.exceptions import BadRequest

from db.client.core import DatabaseClient
from endpoints.instantiations.auth_.resend_validation_email.dto import EmailOnlyDTO
from endpoints.instantiations.auth_.signup.middleware import (
    get_validation_token_jwt,
    send_signup_link,
    _validation_email_sent_response,
)
from middleware.primary_resource_logic.api_key import generate_token


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

    return _validation_email_sent_response(email=email)
