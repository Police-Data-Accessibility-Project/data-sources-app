import json

from flask import redirect, url_for, request, session
from flask_restx import fields

#
#
from config import oauth
from resources.PsycopgResource import PsycopgResource
from utilities.namespace import create_namespace, AppNamespaces

namespace_auth = create_namespace(AppNamespaces.AUTH)

AUTHORIZATION_URL = "your_authorization_url"
REDIRECT_URI = "your_redirect_uri"


authorize_input_model = namespace_auth.model(
    "AuthorizeInput",
    {
        "destination_page": fields.String(
            description="The page to redirect the user to after authorization",
            example="/",
        ),
        "callback_function": fields.String(
            description="The function to call after authorization",
            example="login_user",
        ),
        "callback_params": fields.Raw(
            description="The parameters to pass to the callback function. Take form of a dictionary stringified",
            example="{'username': 'john', 'password': 'secret'}",
        ),
    },
)

@namespace_auth.route("/authorize")
class Authorize(PsycopgResource):

    @namespace_auth.doc(
        description="Use OAuth2 to authorize the user via Github. After authentication, redirects to `callback` "
                    "endpoint` with `original_page` parameter.",
        responses={
            302: 'Redirect to Github authorization page',
            400: 'Bad Request',
            500: 'Internal Server Error'
        }
    )
    @namespace_auth.expect(authorize_input_model)
    def get(self):
        """
        Use OAuth2 to authorize the user via Github
        :return:
        """
        # Get original page
        original_page = request.args.get("original_page") or '/'
        session["original_page"] = original_page

        redirect_uri = url_for(
            endpoint="auth_callback",
            _external=True,
        )
        return oauth.github.authorize_redirect(
            endpoint=redirect_uri,
        )


@namespace_auth.route("/callback")
class Callback(PsycopgResource):

    def get(self):
        print("Starting get request")
        print(request.args)
        token = oauth.github.authorize_access_token()
        user_id = get_github_user_email(token)
        print(f"User id: {user_id}")

        # TODO: Implement your logic here

        return redirect(session.pop("original_page", '/'))


def get_github_user_email(token: str) -> str:
    response = oauth.github.get("user/emails", token=token)
    print(f"Response: {response}")
    response.raise_for_status()
    print(f"Response json: {response.json()}")
    emails = response.json()

    return emails[0]["email"]
