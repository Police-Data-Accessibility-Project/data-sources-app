from marshmallow import RAISE

from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.agencies.post import AgenciesPostDTO
from middleware.schema_and_dto.schemas.agencies.post import AgenciesPostSchema

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
