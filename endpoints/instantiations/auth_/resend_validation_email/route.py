from http import HTTPStatus

from endpoints._helpers.response_info import ResponseInfo
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints.instantiations.auth_.resend_validation_email.endpoint_schema_config import (
    AuthResendValidationEmailEndpointSchemaConfig,
)
from middleware.decorators.endpoint_info import endpoint_info
from endpoints.instantiations.auth_.resend_validation_email.middleware import (
    resend_validation_email_wrapper,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import NO_AUTH_INFO
from utilities.namespace import create_namespace, AppNamespaces

namespace_resend_validation_email = create_namespace(
    namespace_attributes=AppNamespaces.AUTH
)


@namespace_resend_validation_email.route("/resend-validation-email")
class ResendValidationEmail(PsycopgResource):
    @endpoint_info(
        namespace=namespace_resend_validation_email,
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
