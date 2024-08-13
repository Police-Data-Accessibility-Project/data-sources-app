from config import limiter
from middleware.callback_flask_sessions_logic import setup_callback_session
from middleware.enums import CallbackFunctionsEnum
from middleware.callback_oauth_logic import redirect_to_github_authorization
from resources.PsycopgResource import PsycopgResource
from utilities.namespace import create_namespace, AppNamespaces

namespace_login_with_github = create_namespace(AppNamespaces.AUTH)

@namespace_login_with_github.route("/login-with-github")
class LoginWithGithub(PsycopgResource):

    @namespace_login_with_github.doc(
        description="""
        Login the user to their Github account.
        Must be run within the browser. Cannot be run by direct api calls.
        To test, click "Try it out", type in parameters, copy URL in generated CURL request
         and paste in browser. 
        Overall function is comparable to `/login` endpoint.
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
        Login the user with their Github account
        :return:
        """
        setup_callback_session(
            callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB,
        )
        return redirect_to_github_authorization()
