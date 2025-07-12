from http import HTTPStatus

from flask import Response

from endpoints._helpers.response_info import ResponseInfo
from endpoints.instantiations.auth_.signup.route import namespace_signup
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints.schema_config.instantiations.auth.resend_validate_email import (
    AuthResendValidationEmailEndpointSchemaConfig,
)
from middleware.decorators.endpoint_info import endpoint_info
from middleware.primary_resource_logic.api_key import create_api_key_for_user
from middleware.primary_resource_logic.signup import (
    validate_email_wrapper,
    resend_validation_email_wrapper,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.access_info.validate_email import ValidateEmailTokenAccessInfo
from middleware.security.auth.info.instantiations import (
    STANDARD_JWT_AUTH_INFO,
    NO_AUTH_INFO,
    VALIDATE_EMAIL_AUTH_INFO,
)
from utilities.namespace import create_namespace, AppNamespaces

namespace_auth = create_namespace(namespace_attributes=AppNamespaces.AUTH)
API_KEY_ROUTE = "/api-key"


@namespace_auth.route(API_KEY_ROUTE)
class ApiKeyResource(PsycopgResource):
    """Represents a resource for generating an API key for authenticated users."""

    @endpoint_info(
        namespace=namespace_auth,
        auth_info=STANDARD_JWT_AUTH_INFO,
        description="Generates an API key for authenticated users.",
        response_info=ResponseInfo(
            success_message="OK. API key generated.",
        ),
        schema_config=SchemaConfigs.API_KEY_POST,
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        """
        Authenticates a user based on provided credentials and generates an API key.

        Reads the 'email' and 'password' from the JSON body of the request, validates the user,
        and if successful, generates and returns a new API key.

        If the email and password match a row in the database, a new API key is created using uuid.uuid4().hex, updated in for the matching user in the users table, and the API key is sent to the user.

        Returns:
        - dict: A dictionary containing the generated API key, or None if an error occurs.
        """
        return self.run_endpoint(
            wrapper_function=create_api_key_for_user,
            access_info=access_info,
        )


@namespace_auth.route("/validate-email")
class ValidateEmail(PsycopgResource):
    @endpoint_info(
        namespace=namespace_signup,
        auth_info=VALIDATE_EMAIL_AUTH_INFO,
        description="Validate email address and log in user.",
        response_info=ResponseInfo(
            success_message="User validated and logged in.",
        ),
        schema_config=SchemaConfigs.AUTH_VALIDATE_EMAIL,
    )
    def post(
        self,
        access_info: ValidateEmailTokenAccessInfo,
    ):
        return self.run_endpoint(
            wrapper_function=validate_email_wrapper, access_info=access_info
        )


@namespace_auth.route("/resend-validation-email")
class ResendValidationEmail(PsycopgResource):
    @endpoint_info(
        namespace=namespace_signup,
        auth_info=NO_AUTH_INFO,
        description="Resend validation email",
        response_info=ResponseInfo(
            response_dictionary={
                HTTPStatus.OK.value: "OK. Validation email sent.",
                HTTPStatus.BAD_REQUEST.value: "User email does not exist or is not pending validation.",
                HTTPStatus.INTERNAL_SERVER_ERROR.value: "Internal server error",
            }
        ),
        schema_config=SchemaConfigs.AUTH_RESEND_VALIDATION_EMAIL,
    )
    def post(
        self,
        access_info: AccessInfoPrimary,
    ):
        return self.run_endpoint(
            wrapper_function=resend_validation_email_wrapper,
            schema_populate_parameters=AuthResendValidationEmailEndpointSchemaConfig.get_schema_populate_parameters(),
        )
