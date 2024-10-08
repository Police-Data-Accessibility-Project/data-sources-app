from flask import Response

from middleware.primary_resource_logic.search_logic import (
    search_wrapper,
    SearchRequests,
    SearchRequestSchema,
)
from middleware.decorators import api_key_required
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from resources.resource_helpers import add_api_key_header_arg, create_search_model
from middleware.schema_and_dto_logic.dynamic_schema_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from utilities.namespace import create_namespace, AppNamespaces

namespace_search = create_namespace(namespace_attributes=AppNamespaces.SEARCH)

doc_info = get_restx_param_documentation(
    namespace=namespace_search,
    schema=SearchRequestSchema,
    model_name="SearchRequest",
)
request_parser = doc_info.parser
add_api_key_header_arg(request_parser)
search_response_model = create_search_model(namespace_search)


@namespace_search.route("/search-location-and-record-type")
class Search(PsycopgResource):
    """
    Provides a resource for performing searches in the database for data sources
    based on user-provided search terms and location.
    """

    @api_key_required
    @handle_exceptions
    @namespace_search.expect(request_parser)
    @namespace_search.response(200, "Success", search_response_model)
    @namespace_search.response(500, "Internal server error")
    @namespace_search.response(400, "Bad request; missing or bad API key")
    @namespace_search.response(403, "Forbidden; invalid API key")
    def get(self) -> Response:
        """
        Performs a search using the provided search terms and location.

        Performs a search using the provided record type and location parameters.
        It attempts to find relevant data sources in the database.

        Record Types:
        - "Police & Public Interactions"
        - "Info about Officers"
        - "Info about Agencies"
        - "Agency-published Resources"
        - "Jails & Courts"

        Source of truth for record types can be found at https://app.gitbook.com/o/-MXypK5ySzExtEzQU6se/s/-MXyolqTg_voOhFyAcr-/activities/data-dictionaries/record-types-taxonomy

        Returns:
        - A dictionary containing a message about the search results and the data found, if any.
        """
        return self.run_endpoint(
            wrapper_function=search_wrapper,
            schema_populate_parameters=SchemaPopulateParameters(
                schema=SearchRequestSchema(),
                dto_class=SearchRequests,
            ),
        )
