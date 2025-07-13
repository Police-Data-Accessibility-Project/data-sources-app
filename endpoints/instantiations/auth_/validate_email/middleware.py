from db.client.core import DatabaseClient
from middleware.primary_resource_logic.login_queries import access_and_refresh_token_response
from middleware.security.access_info.validate_email import ValidateEmailTokenAccessInfo


def validate_email_wrapper(
    db_client: DatabaseClient, access_info: ValidateEmailTokenAccessInfo
):
    email = db_client.validate_and_add_user(access_info.validate_email_token)

    return access_and_refresh_token_response(
        email=email,
        message="Successfully validated email and logged in.",
    )
