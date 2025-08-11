from marshmallow import RAISE

from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.instantiations.agencies_.post.dto import AgenciesPostDTO
from endpoints.instantiations.agencies_.post.schemas.outer import AgenciesPostSchema

ProposalAgenciesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=AgenciesPostSchema(
        exclude=[
            "agency_info.approval_status",
            "agency_info.last_approval_editor",
            "agency_info.submitter_contact",
            "agency_info.rejection_reason",
        ],
        unknown=RAISE,
    ),
    input_dto_class=AgenciesPostDTO,
)
