from flask import Response

from endpoints.schema_config.instantiations.match import MatchAgencyEndpointSchemaConfig
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import STANDARD_JWT_AUTH_INFO
from middleware.decorators.endpoint_info import endpoint_info
from middleware.primary_resource_logic.match import (
    match_agency_wrapper,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
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
            schema_populate_parameters=MatchAgencyEndpointSchemaConfig.get_schema_populate_parameters(),
        )
