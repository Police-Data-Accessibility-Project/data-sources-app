from flask import Response

from middleware.access_logic import AccessInfo, NO_AUTH_INFO
from middleware.decorators import authentication_required, endpoint_info_2
from middleware.enums import AccessTypeEnum
from middleware.primary_resource_logic.unique_url_checker import (
    UniqueURLCheckerRequestSchema,
    UniqueURLCheckerResponseOuterSchema,
    unique_url_checker_wrapper,
    UniqueURLCheckerRequestDTO,
)
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from resources.endpoint_schema_config import EndpointSchemaConfig, SchemaConfigs
from resources.resource_helpers import add_api_key_header_arg, ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_url_checker = create_namespace(namespace_attributes=AppNamespaces.CHECK)


@namespace_url_checker.route("/unique-url")
class UniqueURLChecker(PsycopgResource):

    @endpoint_info_2(
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
    def get(self, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            wrapper_function=unique_url_checker_wrapper,
            schema_populate_parameters=SchemaConfigs.CHECKER_GET.value.get_schema_populate_parameters(),
        )
