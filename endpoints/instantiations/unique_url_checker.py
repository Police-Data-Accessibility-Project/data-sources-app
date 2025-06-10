from flask import Response

from config import limiter
from endpoints.schema_config.instantiations.checker import (
    UniqueURLCheckerEndpointSchemaConfig,
)
from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import NO_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.unique_url_checker import (
    unique_url_checker_wrapper,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_url_checker = create_namespace(namespace_attributes=AppNamespaces.CHECK)


@namespace_url_checker.route("/unique-url")
class UniqueURLChecker(PsycopgResource):

    @endpoint_info(
        namespace=namespace_url_checker,
        description="Check if a URL is unique",
        schema_config=SchemaConfigs.CHECKER_GET,
        auth_info=NO_AUTH_INFO,
        response_info=ResponseInfo(
            response_dictionary={
                200: "OK. Returns duplicate urls if they exist.",
                500: "Internal server error",
            }
        ),
    )
    @limiter.exempt
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=unique_url_checker_wrapper,
            schema_populate_parameters=UniqueURLCheckerEndpointSchemaConfig.get_schema_populate_parameters(),
        )
