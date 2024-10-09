from flask import Response

from middleware.access_logic import AccessInfo
from middleware.decorators import authentication_required
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
from resources.resource_helpers import add_api_key_header_arg
from utilities.namespace import create_namespace, AppNamespaces

namespace_url_checker = create_namespace(namespace_attributes=AppNamespaces.CHECK)

request_doc_info = get_restx_param_documentation(
    namespace=namespace_url_checker,
    schema=UniqueURLCheckerRequestSchema,
)

response_doc_info = get_restx_param_documentation(
    namespace=namespace_url_checker,
    schema=UniqueURLCheckerResponseOuterSchema,
)
add_api_key_header_arg(request_doc_info.parser)


@namespace_url_checker.route("/unique-url")
class UniqueURLChecker(PsycopgResource):

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.API_KEY],
    )
    @namespace_url_checker.doc(
        description="Check if a URL is unique",
        responses={
            200: ("OK. Returns duplicate urls if they exist.", response_doc_info.model),
            500: "Internal server error",
        },
        expect=[request_doc_info.parser],
    )
    def get(self, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            wrapper_function=unique_url_checker_wrapper,
            schema_populate_parameters=SchemaPopulateParameters(
                schema=UniqueURLCheckerRequestSchema(),
                dto_class=UniqueURLCheckerRequestDTO,
            ),
        )
