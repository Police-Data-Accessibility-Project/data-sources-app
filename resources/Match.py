from flask import Response

from middleware.access_logic import STANDARD_JWT_AUTH_INFO, AccessInfoPrimary
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.match_logic import try_matching_agency, match_agency_wrapper
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
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
        description="Returns agencies, if any, that match or partially match the search criteria",
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=match_agency_wrapper,
            schema_populate_parameters=SchemaConfigs.MATCH_AGENCY.value.get_schema_populate_parameters(),
        )
