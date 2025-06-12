from http import HTTPStatus

from config import limiter
from endpoints.schema_config.instantiations.auth.github.link import (
    AuthGithubLinkEndpointSchemaConfig,
)
from middleware.access_logic import AccessInfoPrimary
from middleware.security.authentication_info import NO_AUTH_INFO
from middleware.decorators.decorators import endpoint_info

from middleware.primary_resource_logic.github_oauth import (
    link_github_account_request_wrapper,
)

from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
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
        return self.run_endpoint(
            wrapper_function=link_github_account_request_wrapper,
            schema_populate_parameters=AuthGithubLinkEndpointSchemaConfig.get_schema_populate_parameters(),
        )
