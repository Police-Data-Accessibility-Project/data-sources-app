from http import HTTPStatus

from config import limiter
from database_client.database_client import DatabaseClient
from middleware.access_logic import NO_AUTH_INFO, AccessInfoPrimary
from middleware.decorators import endpoint_info

from middleware.primary_resource_logic.github_oauth_logic import (
    link_github_account_request_wrapper,
)

from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_request_content_population import (
    populate_schema_with_request_content,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_link_to_github = create_namespace(AppNamespaces.OAUTH)


@namespace_link_to_github.route("/link-to-github")
class LinkToGithub(PsycopgResource):

    @endpoint_info(
        namespace=namespace_link_to_github,
        auth_info=NO_AUTH_INFO,
        schema_config=SchemaConfigs.AUTH_GITHUB_LINK,
        response_info=ResponseInfo(
            response_dictionary={
                HTTPStatus.OK.value: "Accounts linked.",
                HTTPStatus.UNAUTHORIZED.value: "Unauthorized. Forbidden or invalid authentication.",
                HTTPStatus.INTERNAL_SERVER_ERROR.value: "Internal Server Error.",
            },
        ),
        description="""
        Link the user to their Github account.
        Must be run within the browser. Cannot be run by direct api calls.
        To test, click "Try it out", type in parameters, copy URL in generated CURL request
         and paste in browser. 
         
        (Note if testing locally, the root domain in the url MUST match the one specified
         in your Homepage URL for the Github OAuth application; e.g., if "localhost:5000", you must query on 
         "localhost:5000" and NOT "127.0.0.1:5000"; doing other wise can lead to CSRF errors)
        
        """,
    )
    @limiter.limit("5 per minute")
    def post(self, access_info: AccessInfoPrimary):
        """
        Link the user to their Github account
        :return:
        """
        dto = populate_schema_with_request_content(
            schema=SchemaConfigs.AUTH_GITHUB_LINK.value.input_schema,
            dto_class=SchemaConfigs.AUTH_GITHUB_LINK.value.input_dto_class,
        )
        return link_github_account_request_wrapper(
            db_client=DatabaseClient(),
            dto=dto,
        )
