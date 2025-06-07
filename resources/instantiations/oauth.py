from http import HTTPStatus

from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import NO_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.enums import CallbackFunctionsEnum
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_request_content_population import (
    populate_schema_with_request_content,
)
from middleware.schema_and_dto_logic.dtos.github.oauth import GithubOAuthRequestDTO
from middleware.third_party_interaction_logic.callback_flask_sessions_logic import (
    setup_callback_session,
)
from middleware.third_party_interaction_logic.callback_oauth_logic import (
    redirect_to_github_authorization,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
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
        dto: GithubOAuthRequestDTO = populate_schema_with_request_content(
            schema=SchemaConfigs.AUTH_GITHUB_OAUTH.value.input_schema,
            dto_class=SchemaConfigs.AUTH_GITHUB_OAUTH.value.input_dto_class,
        )
        setup_callback_session(
            callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB,
            redirect_url=dto.redirect_url,
        )
        return redirect_to_github_authorization()
