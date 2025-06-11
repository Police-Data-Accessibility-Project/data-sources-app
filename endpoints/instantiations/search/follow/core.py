from endpoints._helpers.response_info import ResponseInfo
from endpoints.instantiations.search.namespace import namespace_search
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints.schema_config.instantiations.search.follow.delete import (
    SearchFollowDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.post import (
    SearchFollowPostEndpointSchemaConfig,
)
from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import API_OR_JWT_AUTH_INFO, STANDARD_JWT_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.search.wrappers.follow.get import (
    get_followed_searches,
)
from middleware.primary_resource_logic.search.wrappers.follow.create import (
    create_followed_search,
)
from middleware.primary_resource_logic.search.wrappers.follow.delete import (
    delete_followed_search,
)


@namespace_search.route("/follow")
class SearchFollow(PsycopgResource):
    """
    A resource for following and unfollowing searches, as well as retrieving followed searches.
    """

    @endpoint_info(
        namespace=namespace_search,
        auth_info=API_OR_JWT_AUTH_INFO,
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

    @endpoint_info(
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
            schema_populate_parameters=SearchFollowPostEndpointSchemaConfig.get_schema_populate_parameters(),
            access_info=access_info,
        )

    @endpoint_info(
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
            schema_populate_parameters=SearchFollowDeleteEndpointSchemaConfig.get_schema_populate_parameters(),
            access_info=access_info,
        )
