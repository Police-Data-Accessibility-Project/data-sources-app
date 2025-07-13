from endpoints._helpers.response_info import ResponseInfo
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from middleware.decorators.endpoint_info import endpoint_info
from endpoints.instantiations.auth_.validate_email.middleware import validate_email_wrapper
from middleware.security.access_info.validate_email import ValidateEmailTokenAccessInfo
from middleware.security.auth.info.instantiations import VALIDATE_EMAIL_AUTH_INFO
from utilities.namespace import AppNamespaces, create_namespace

namespace_validate_email = create_namespace(namespace_attributes=AppNamespaces.AUTH)
ROUTE = "/validate-email"


@namespace_validate_email.route(ROUTE)
class ValidateEmail(PsycopgResource):
    @endpoint_info(
        namespace=namespace_validate_email,
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
