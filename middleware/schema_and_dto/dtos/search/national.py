from pydantic import BaseModel, model_validator
from werkzeug.exceptions import BadRequest

from middleware.enums import RecordTypes
from middleware.schema_and_dto.dtos._helpers import default_field_not_required
from utilities.enums import RecordCategories


class SearchFollowNationalRequestDTO(BaseModel):
    record_categories: list[RecordCategories] = default_field_not_required(
        description="Selected record categories."
    )
    record_types: list[RecordTypes] = default_field_not_required(
        description="Selected record types."
    )

    @model_validator(mode="before")
    def check_exclusive_fields(cls, values):
        record_categories = values.get("record_categories")
        record_types = values.get("record_types")
        if record_categories is None and record_types is None:
            raise BadRequest(
                "One of record_categories or record_types must be provided."
            )
        if record_categories is not None and record_types is not None:
            raise BadRequest(
                "Only one of record_categories or record_types can be provided."
            )
        return values
