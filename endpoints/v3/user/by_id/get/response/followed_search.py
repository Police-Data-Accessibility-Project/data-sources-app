from pydantic import BaseModel, Field

from db.enums import LocationType
from endpoints.v3.user.by_id.get.response.location import GetUserSearchLocationModel
from middleware.enums import RecordTypesEnum
from utilities.enums import RecordCategoryEnum


class GetUserFollowedSearchModel(BaseModel):
    display_name: str = Field(
        description="The display name of the followed search.",
    )

    # Individual Location Components
    location_info: GetUserSearchLocationModel = Field(
        description="The location info of the recent search.",
    )

    # Record Types and Categories
    record_types: list[RecordTypesEnum] = Field(
        description="The record types of the followed search.",
    )
    record_categories: list[RecordCategoryEnum] = Field(
        description="The record categories of the followed search.",
    )
    record_types_by_category: dict[RecordCategoryEnum, RecordTypesEnum] = Field(
        description="The record types of the followed search grouped by category.",
    )
