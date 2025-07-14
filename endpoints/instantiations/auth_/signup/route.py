from http import HTTPStatus

from endpoints._helpers.response_info import ResponseInfo
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints.instantiations.auth_.signup.endpoint_schema_config import (
    AuthSignupEndpointSchemaConfig,
)
from middleware.decorators.endpoint_info import endpoint_info
from endpoints.instantiations.auth_.signup.middleware import signup_wrapper
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import NO_AUTH_INFO
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
            schema_populate_parameters=AuthSignupEndpointSchemaConfig.get_schema_populate_parameters(),
        )
