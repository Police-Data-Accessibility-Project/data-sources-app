from endpoints.instantiations.user.by_id.patch.dto import UserPatchDTO
from endpoints.instantiations.user.by_id.patch.schema import UserPatchSchema
from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.common.common_response_schemas import MessageSchema

UserPatchEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=UserPatchSchema(),
    input_dto_class=UserPatchDTO,
    primary_output_schema=MessageSchema()
)