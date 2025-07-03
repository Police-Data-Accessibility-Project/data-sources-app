from http import HTTPStatus

from middleware.schema_and_dto.dynamic.dto_request_content_population import (
    populate_dto_with_request_content,
)
from middleware.schema_and_dto.non_dto_dataclasses import DTOPopulateParameters
from middleware.schema_and_dto.schemas.auth.github.oauth import GithubOAuthRequestSchema
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import NO_AUTH_INFO
from middleware.decorators.endpoint_info import endpoint_info
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
from utilities.enums import SourceMappingEnum
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
        dto_populate_parameters = DTOPopulateParameters(
            dto_class=GithubOAuthRequestDTO,
            source=SourceMappingEnum.QUERY_ARGS,
            validation_schema=GithubOAuthRequestSchema,
        )

        dto: GithubOAuthRequestDTO = populate_dto_with_request_content(
            dto_populate_parameters
        )
        setup_callback_session(
            callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB,
            redirect_url=dto.redirect_url,
        )
        return redirect_to_github_authorization()
