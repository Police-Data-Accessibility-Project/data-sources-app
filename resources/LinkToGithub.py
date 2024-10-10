from flask_restx import reqparse

from config import limiter
from middleware.third_party_interaction_logic.callback_flask_sessions_logic import setup_callback_session
from middleware.primary_resource_logic.callback_primary_logic import LinkToGithubRequest
from middleware.enums import CallbackFunctionsEnum
from middleware.third_party_interaction_logic.callback_oauth_logic import redirect_to_github_authorization
from resources.PsycopgResource import PsycopgResource
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
    @namespace_link_to_github.doc(
        description="""
        Link the user to their Github account.
        Must be run within the browser. Cannot be run by direct api calls.
        To test, click "Try it out", type in parameters, copy URL in generated CURL request
         and paste in browser. 
        """,
        responses={
            302: "Redirect to Github",
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    @limiter.limit("5 per minute")
    def post(self):
        """
        Link the user to their Github account
        :return:
        """
        dto = populate_dto_with_request_content(
            dto_class=LinkToGithubRequest,
            source=SourceMappingEnum.JSON,
        )
        setup_callback_session(
            callback_functions_enum=CallbackFunctionsEnum.LINK_TO_GITHUB,
            redirect_to=dto.redirect_to,
            user_email=dto.user_email,
        )
        return redirect_to_github_authorization()
