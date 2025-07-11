"""
These schemas are used in response validation,
and do not have DTOs associated with them.
"""

from middleware.schema_and_dto.dtos.common_dtos import MessageDTO, IDAndMessageDTO, \
    GetManyResponseDTOBase, GetManyResponseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow

MessageSchema = pydantic_to_marshmallow(MessageDTO)

IDAndMessageSchema = pydantic_to_marshmallow(IDAndMessageDTO)

GetManyResponseSchemaBase = pydantic_to_marshmallow(GetManyResponseDTOBase)

GetManyResponseSchema = pydantic_to_marshmallow(GetManyResponseDTO)
