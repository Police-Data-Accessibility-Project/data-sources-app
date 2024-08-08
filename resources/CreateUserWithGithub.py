from config import limiter
from middleware.callback_flask_sessions_logic import setup_callback_session
from middleware.callback_oauth_logic import redirect_to_github_authorization
from middleware.enums import CallbackFunctionsEnum
from resources.PsycopgResource import PsycopgResource
from resources.User import namespace_user
from utilities.namespace import create_namespace, AppNamespaces

namespace_create_user_with_github = create_namespace(AppNamespaces.AUTH)

@namespace_create_user_with_github.route("/create-user-with-github")
class CreateUserWithGithub(PsycopgResource):

    @namespace_user.doc(
        description="""
        Creates a new user with Github account
        """,
        responses={
            201: "Created",
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    @limiter.limit("5 per minute")
    def post(self):
        """
        Creates a new user with Github account
        :return:
        """
        setup_callback_session(
            callback_functions_enum=CallbackFunctionsEnum.CREATE_USER_WITH_GITHUB
        )
        return redirect_to_github_authorization()
