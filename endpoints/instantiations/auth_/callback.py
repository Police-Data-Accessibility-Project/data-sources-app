from config import limiter
from middleware.primary_resource_logic.callback import (
    callback_outer_wrapper,
)
from endpoints.psycopg_resource import PsycopgResource
from utilities.namespace import create_namespace, AppNamespaces

namespace_callback = create_namespace(AppNamespaces.AUTH)


@namespace_callback.route("/callback")
class Callback(PsycopgResource):
    @namespace_callback.doc(
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
