from endpoints.instantiations.data_requests_._shared.dtos.get import (
    DataRequestsGetDTOBase,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

DataRequestsGetSchemaBase = pydantic_to_marshmallow(DataRequestsGetDTOBase)
