from http import HTTPStatus

from endpoints.schema_config.instantiations.auth.github.oauth import (
    AuthGitHubOAuthEndpointSchemaConfig,
)
from middleware.access_logic import AccessInfoPrimary
from middleware.security.authentication_info import NO_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.enums import CallbackFunctionsEnum
from middleware.schema_and_dto.dtos.github.oauth import GithubOAuthRequestDTO
from middleware.third_party_interaction_logic.callback.flask_sessions import (
    setup_callback_session,
)
from middleware.third_party_interaction_logic.callback.oauth import (
    redirect_to_github_authorization,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_oauth = create_namespace(AppNamespaces.OAUTH)


@namespace_oauth.route("/github")
class GithubOAuth(PsycopgResource):

    @endpoint_info(
        namespace=namespace_oauth,
        auth_info=NO_AUTH_INFO,
        schema_config=SchemaConfigs.AUTH_GITHUB_OAUTH,
        response_info=ResponseInfo(
            response_dictionary={
                HTTPStatus.FOUND.value: "Returns redirect link to OAuth.",
                HTTPStatus.INTERNAL_SERVER_ERROR.value: "Internal Server Error.",
            }
        ),
        description="Directs user to OAuth page for App.",
    )
    def get(self, access_info: AccessInfoPrimary):
        dto: GithubOAuthRequestDTO = (
            AuthGitHubOAuthEndpointSchemaConfig.populate_schema_with_request_content()
        )
        setup_callback_session(
            callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB,
            redirect_url=dto.redirect_url,
        )
        return redirect_to_github_authorization()
