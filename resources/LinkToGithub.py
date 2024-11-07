from http import HTTPStatus

from flask_restx import reqparse
from marshmallow import Schema

from config import limiter
from middleware.access_logic import NO_AUTH_INFO, AccessInfo
from middleware.decorators import endpoint_info_2
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_request_content_population import (
    populate_schema_with_request_content,
)
from middleware.third_party_interaction_logic.callback_flask_sessions_logic import (
    setup_callback_session,
)
from middleware.primary_resource_logic.callback_primary_logic import (
    LinkToGithubRequestDTO,
)
from middleware.enums import CallbackFunctionsEnum
from middleware.third_party_interaction_logic.callback_oauth_logic import (
    redirect_to_github_authorization,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_dto_request_content_population import (
    populate_dto_with_request_content,
)
from utilities.enums import SourceMappingEnum

namespace_link_to_github = create_namespace(AppNamespaces.AUTH)

link_to_github_parser = reqparse.RequestParser()
link_to_github_parser.add_argument(
    "redirect_to",
    type=str,
    required=True,
    help="The URL to redirect the user to after linking to Github",
    default="/",
)
link_to_github_parser.add_argument(
    "user_email",
    type=str,
    required=True,
    help="The email of the user. Used to identify the user to link with. Must match the primary email of the Github account.",
)


@namespace_link_to_github.route("/link-to-github")
class LinkToGithub(PsycopgResource):

    @namespace_link_to_github.expect(link_to_github_parser)
    @endpoint_info_2(
        namespace=namespace_link_to_github,
        auth_info=NO_AUTH_INFO,
        schema_config=SchemaConfigs.AUTH_GITHUB_LINK,
        response_info=ResponseInfo(
            response_dictionary={
                HTTPStatus.OK: "Callback response. Accounts linked.",
                HTTPStatus.FOUND: "Returns redirect link to OAuth.",
                HTTPStatus.INTERNAL_SERVER_ERROR: "Internal Server Error.",
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
    def post(self, access_info: AccessInfo):
        """
        Link the user to their Github account
        :return:
        """
        dto = populate_schema_with_request_content(
            schema=SchemaConfigs.AUTH_GITHUB_LINK.value.input_schema,
            dto_class=SchemaConfigs.AUTH_GITHUB_LINK.value.input_dto_class,
        )
        setup_callback_session(
            callback_functions_enum=CallbackFunctionsEnum.LINK_TO_GITHUB,
            redirect_to=dto.redirect_to,
            user_email=dto.user_email,
        )
        return redirect_to_github_authorization()
