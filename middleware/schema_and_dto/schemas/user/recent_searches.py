from marshmallow import Schema, fields

from endpoints.instantiations.user._shared.dtos.recent_searches import GetUserRecentSearchesDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.schemas.schema_helpers import (
    create_get_many_schema,
)
from middleware.schema_and_dto.util import get_json_metadata
from utilities.enums import RecordCategories



GetUserRecentSearchesOuterSchema = create_get_many_schema(
    data_list_schema=pydantic_to_marshmallow(GetUserRecentSearchesDTO),
    description="The list of recent searches for the user",
)
