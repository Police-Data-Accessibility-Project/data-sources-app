from endpoints._helpers.response_info import ResponseInfo
from endpoints.instantiations.search import namespace_search
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints.schema_config.instantiations.search.follow.national import (
    SearchFollowNationalEndpointSchemaConfig,
)
from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import STANDARD_JWT_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.search.wrappers.follow.national.follow import (
    follow_national_wrapper,
)
from middleware.primary_resource_logic.search.wrappers.follow.national.unfollow import (
    unfollow_national_wrapper,
)


@namespace_search.route("/follow/national")
class SearchFollowNational(PsycopgResource):

    @endpoint_info(
        namespace=namespace_search,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_FOLLOW_NATIONAL,
        response_info=ResponseInfo(success_message="Follows a national search."),
        description="Follows a national search.",
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=follow_national_wrapper,
            schema_populate_parameters=SearchFollowNationalEndpointSchemaConfig.get_schema_populate_parameters(),
            access_info=access_info,
        )

    @endpoint_info(
        namespace=namespace_search,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_FOLLOW_NATIONAL,
        response_info=ResponseInfo(success_message="Unfollows a national search."),
        description="Unfollows a national search.",
    )
    def delete(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=unfollow_national_wrapper,
            schema_populate_parameters=SearchFollowNationalEndpointSchemaConfig.get_schema_populate_parameters(),
            access_info=access_info,
        )
