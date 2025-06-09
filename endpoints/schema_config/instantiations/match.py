from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.match.request import AgencyMatchRequestDTO
from middleware.schema_and_dto.schemas.match.request import AgencyMatchSchema
from middleware.schema_and_dto.schemas.match.response import MatchAgencyResponseSchema

MatchAgencyEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=AgencyMatchSchema(),
    input_dto_class=AgencyMatchRequestDTO,
    primary_output_schema=MatchAgencyResponseSchema(),
)
