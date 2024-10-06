from config import limiter
from middleware.callback_primary_logic import (
    callback_outer_wrapper,
)
from resources.PsycopgResource import PsycopgResource
from utilities.namespace import create_namespace, AppNamespaces

namespace_auth = create_namespace(AppNamespaces.AUTH)


@namespace_auth.route("/callback")
class Callback(PsycopgResource):
    @namespace_auth.doc(
        description="""
            Callback function for multiple endpoints.
            Designed to be called by the Github OAuth2 callback function
            and not by the user or app directly.
            """
    )
    @limiter.limit("1000000 per second")
    def get(self):
        """
        Receive the Callback from Github
        :return:
        """
        return self.run_endpoint(callback_outer_wrapper)
