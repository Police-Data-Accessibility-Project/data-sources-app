from flask import Response

from middleware.access_logic import (
    GET_AUTH_INFO,
    WRITE_ONLY_AUTH_INFO,
    STANDARD_JWT_AUTH_INFO,
    AccessInfoPrimary,
    NO_AUTH_INFO,
)
from middleware.primary_resource_logic.search_logic import (
    search_wrapper,
    get_followed_searches,
    delete_followed_search,
    create_followed_search,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.search_schemas import (
    SearchRequestSchema,
    SearchRequests,
)
from middleware.decorators import api_key_required, endpoint_info_2
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import (
    add_api_key_header_arg,
    create_search_model,
    ResponseInfo,
)
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from utilities.namespace import create_namespace, AppNamespaces

namespace_search = create_namespace(namespace_attributes=AppNamespaces.SEARCH)


@namespace_search.route("/search-location-and-record-type")
class Search(PsycopgResource):
    """
    Provides a resource for performing searches in the database for data sources
    based on user-provided search terms and location.
    """

    @endpoint_info_2(
        namespace=namespace_search,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_LOCATION_AND_RECORD_TYPE_GET,
        response_info=ResponseInfo(success_message="Search successful."),
        description="Performs a search using the provided search terms and location.",
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Performs a search using the provided search terms and location.

        Performs a search using the provided record type and location parameters.

        It attempts to find relevant data sources in the database.

        Source of truth for record types can be found at https://app.gitbook.com/o/-MXypK5ySzExtEzQU6se/s/-MXyolqTg_voOhFyAcr-/activities/data-dictionaries/record-types-taxonomy

        Returns:
        - A dictionary containing a message about the search results and the data found, if any.
        """
        return self.run_endpoint(
            wrapper_function=search_wrapper,
            access_info=access_info,
            schema_populate_parameters=SchemaConfigs.SEARCH_LOCATION_AND_RECORD_TYPE_GET.value.get_schema_populate_parameters(),
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
    def get(self, access_info: AccessInfoPrimary):
        """
        Retrieves the searches that the user follows.
        :return:
        """
        return self.run_endpoint(
            wrapper_function=get_followed_searches, access_info=access_info
        )

    @endpoint_info_2(
        namespace=namespace_search,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_FOLLOW_POST,
        response_info=ResponseInfo(
            success_message="Returns result of search follow request."
        ),
        description="Follows a search.",
    )
    def post(self, access_info: AccessInfoPrimary):
        """
        Follows a search.
        :return:
        """
        return self.run_endpoint(
            wrapper_function=create_followed_search,
            schema_populate_parameters=SchemaConfigs.SEARCH_FOLLOW_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )

    @endpoint_info_2(
        namespace=namespace_search,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_FOLLOW_DELETE,
        response_info=ResponseInfo(
            success_message="Returns result of search unfollow request."
        ),
        description="Unfollows a search.",
    )
    def delete(self, access_info: AccessInfoPrimary):
        """
        Unfollows a search.
        :return:
        """
        return self.run_endpoint(
            wrapper_function=delete_followed_search,
            schema_populate_parameters=SchemaConfigs.SEARCH_FOLLOW_DELETE.value.get_schema_populate_parameters(),
            access_info=access_info,
        )
