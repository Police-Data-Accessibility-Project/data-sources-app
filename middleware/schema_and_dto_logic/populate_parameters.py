from middleware.schema_and_dto_logic.dtos.common.base import (
    GetManyRequestsBaseSchema,
    GetManyBaseDTO,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters

GET_MANY_SCHEMA_POPULATE_PARAMETERS = SchemaPopulateParameters(
    schema=GetManyRequestsBaseSchema(),
    dto_class=GetManyBaseDTO,
)
