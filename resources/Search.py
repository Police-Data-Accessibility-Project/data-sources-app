from flask import Response

from middleware.access_logic import GET_AUTH_INFO, WRITE_ONLY_AUTH_INFO, OWNER_WRITE_ONLY_AUTH_INFO, AccessInfo
from middleware.primary_resource_logic.search_logic import (
    search_wrapper,
    get_followed_searches, delete_followed_search, create_followed_search,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.search_schemas import SearchRequestSchema, SearchRequests
from middleware.decorators import api_key_required, endpoint_info_2
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import add_api_key_header_arg, create_search_model, ResponseInfo
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
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

    # TODO: Modernize to endpoint_info_2
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

@namespace_search.route("/follow")
class SearchFollow(PsycopgResource):
    """
    A resource for following and unfollowing searches, as well as retrieving followed searches.
    """

    @endpoint_info_2(
        namespace=namespace_search,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_FOLLOW_GET,
        response_info=ResponseInfo(
            success_message="Returns the searches that the user follows."
        ),
        description="Retrieves the searches that the user follows.",
    )
    def get(self, access_info: AccessInfo):
        """
        Retrieves the searches that the user follows.
        :return:
        """
        return self.run_endpoint(
            wrapper_function=get_followed_searches,
            access_info=access_info
        )


    @endpoint_info_2(
        namespace=namespace_search,
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_FOLLOW_POST,
        response_info=ResponseInfo(
            success_message="Returns result of search follow request."
        ),
        description="Follows a search.",
    )
    def post(self, access_info: AccessInfo):
        """
        Follows a search.
        :return:
        """
        return self.run_endpoint(
            wrapper_function=create_followed_search,
            schema_populate_parameters=SchemaConfigs.SEARCH_FOLLOW_POST.value.get_schema_populate_parameters(),
            access_info=access_info
        )


    @endpoint_info_2(
        namespace=namespace_search,
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_FOLLOW_DELETE,
        response_info=ResponseInfo(
            success_message="Returns result of search unfollow request."
        ),
        description="Unfollows a search.",
    )
    def delete(self, access_info: AccessInfo):
        """
        Unfollows a search.
        :return:
        """
        return self.run_endpoint(
            wrapper_function=delete_followed_search,
            schema_populate_parameters=SchemaConfigs.SEARCH_FOLLOW_DELETE.value.get_schema_populate_parameters(),
            access_info=access_info
        )
