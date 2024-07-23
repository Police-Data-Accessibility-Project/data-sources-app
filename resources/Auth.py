from flask import redirect, url_for
#
#
from config import oauth
from resources.PsycopgResource import PsycopgResource
from utilities.namespace import create_namespace, AppNamespaces

namespace_auth = create_namespace(AppNamespaces.AUTH)

AUTHORIZATION_URL = "your_authorization_url"
REDIRECT_URI = "your_redirect_uri"


@namespace_auth.route("/authorize")
class Authorize(PsycopgResource):

    def get(self):
        """
        Use OAuth2 to authorize the user via Github
        :return:
        """
        redirect_uri = url_for("auth_callback", _external=True)
        return oauth.github.authorize_redirect(redirect_uri)

@namespace_auth.route("/callback")
class Callback(PsycopgResource):

    def get(self):
        token = oauth.github.authorize_access_token()
        response = oauth.github.get("user", token=token)
        response.raise_for_status()
        profile = response.json()

        # store_access_token(user_id, token)
        

        # TODO: Implement your logic here
        return redirect('/')


