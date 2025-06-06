from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import STANDARD_JWT_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.proposals import propose_agency
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_proposals = create_namespace(AppNamespaces.PROPOSALS)


@namespace_proposals.route("/agencies", methods=["POST"])
class ProposalsAgencies(PsycopgResource):

    @endpoint_info(
        namespace=namespace_proposals,
        endpoint_description="Submit a proposal for an agency",
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.PROPOSAL_AGENCIES_POST,
        response_info=ResponseInfo(success_message="Proposal successfully submitted."),
        description="Submit a proposal for an agency",
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=propose_agency,
            schema_populate_parameters=SchemaConfigs.PROPOSAL_AGENCIES_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )
