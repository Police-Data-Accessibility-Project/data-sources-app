from http import HTTPStatus

from config import limiter
from middleware.access_logic import NO_AUTH_INFO, AccessInfo
from middleware.decorators import endpoint_info_2
from middleware.primary_resource_logic.github_oauth_logic import login_with_github_wrapper

from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_login_with_github = create_namespace(AppNamespaces.AUTH)


@namespace_login_with_github.route("/login-with-github")
class LoginWithGithub(PsycopgResource):

    @endpoint_info_2(
        namespace=namespace_login_with_github,
        auth_info=NO_AUTH_INFO,
        schema_config=SchemaConfigs.AUTH_GITHUB_LOGIN,
        response_info=ResponseInfo(
            response_dictionary={
                HTTPStatus.OK: "Callback response. User logged in.",
                HTTPStatus.FOUND: "Returns redirect link to OAuth.",
                HTTPStatus.INTERNAL_SERVER_ERROR: "Internal Server Error.",
            },
        ),
        description="""
        Login the user to their Github account.
        
        If user does not exist, they will be created with information from Github Account.
        
        Must be run within the browser. Cannot be run by direct api calls.
        
        To test, click "Try it out", type in parameters, copy URL in generated CURL request
         and paste in browser. 
         
         (Note if testing locally, the root domain in the url MUST match the one specified
         in your Homepage URL for the Github OAuth application; e.g., if "localhost:5000", you must query on 
         "localhost:5000" and NOT "127.0.0.1:5000"; doing other wise can lead to CSRF errors)
        
        Overall function is comparable to `/login` endpoint.
        """,
    )
    @limiter.limit("5 per minute")
    def post(self, access_info: AccessInfo):
        """
        Login the user with their Github account
        :return:
        """
        return self.run_endpoint(
            wrapper_function=login_with_github_wrapper,
            schema_populate_parameters=SchemaConfigs.AUTH_GITHUB_LOGIN.value.get_schema_populate_parameters(),
        )
