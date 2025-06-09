from flask import Response

from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import STANDARD_JWT_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.match import (
    match_agency_wrapper,
)
from endpoints.PsycopgResource import PsycopgResource
from endpoints.endpoint_schema_config import SchemaConfigs
from endpoints.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_match = create_namespace(AppNamespaces.MATCH)


@namespace_match.route("/agency")
class MatchAgencies(PsycopgResource):

    @endpoint_info(
        namespace=namespace_match,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.MATCH_AGENCY,
        response_info=ResponseInfo(
            success_message="Found any possible matches for the search criteria."
        ),
        description="""
        Returns agencies, if any, that match or partially match the search criteria.
        * If locational data is specified, will search only for agencies which correspond to that exact location
        * If locational data is not specified, will search entire database on submitted name only
        Will return the top 10 by order of which have the closest match.
        """,
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=match_agency_wrapper,
            schema_populate_parameters=SchemaConfigs.MATCH_AGENCY.value.get_schema_populate_parameters(),
        )
