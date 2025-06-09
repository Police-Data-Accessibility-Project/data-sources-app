from http import HTTPStatus


from middleware.access_logic import (
    AccessInfoPrimary,
    ValidateEmailTokenAccessInfo,
)
from middleware.authentication_info import NO_AUTH_INFO, VALIDATE_EMAIL_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.signup import (
    resend_validation_email_wrapper,
    signup_wrapper,
    validate_email_wrapper,
)
from endpoints.PsycopgResource import PsycopgResource
from endpoints.endpoint_schema_config import SchemaConfigs
from endpoints.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_signup = create_namespace(AppNamespaces.AUTH)


@namespace_signup.route("/signup")
class Signup(PsycopgResource):

    @endpoint_info(
        namespace=namespace_signup,
        auth_info=NO_AUTH_INFO,
        description="Sign up for an account",
        response_info=ResponseInfo(
            response_dictionary={
                HTTPStatus.OK.value: "OK. User created.",
                HTTPStatus.CONFLICT.value: "User already exists.",
                HTTPStatus.INTERNAL_SERVER_ERROR.value: "Internal server error",
            }
        ),
        schema_config=SchemaConfigs.AUTH_SIGNUP,
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=signup_wrapper,
            schema_populate_parameters=SchemaConfigs.AUTH_SIGNUP.value.get_schema_populate_parameters(),
        )


@namespace_signup.route("/validate-email")
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


@namespace_signup.route("/resend-validation-email")
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
            schema_populate_parameters=SchemaConfigs.AUTH_RESEND_VALIDATION_EMAIL.value.get_schema_populate_parameters(),
        )
