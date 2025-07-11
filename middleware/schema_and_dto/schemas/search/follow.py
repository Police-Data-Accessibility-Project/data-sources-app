from marshmallow import Schema, fields

from endpoints.instantiations.search._shared.dtos.follow import FollowSearchResponseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.schemas.schema_helpers import (
    create_get_many_schema,
)
from middleware.schema_and_dto.util import get_json_metadata

FollowSearchResponseSchema = pydantic_to_marshmallow(FollowSearchResponseDTO)

GetUserFollowedSearchesSchema = create_get_many_schema(
    data_list_schema=FollowSearchResponseSchema,
    description="The searches that the user follows.",
)
