from pydantic import BaseModel, model_validator
from werkzeug.exceptions import BadRequest

from middleware.enums import RecordTypes
from middleware.schema_and_dto.dtos._helpers import default_field_not_required
from middleware.schema_and_dto.dtos.search.base import SearchFollowRequestBaseDTO
from utilities.enums import RecordCategories


class SearchFollowNationalRequestDTO(SearchFollowRequestBaseDTO): ...
