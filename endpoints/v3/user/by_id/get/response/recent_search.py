from datetime import datetime

from pydantic import BaseModel, Field

from db.enums import LocationType
from endpoints.v3.user.by_id.get.response.location import GetUserSearchLocationModel
from middleware.enums import RecordTypesEnum
from utilities.enums import RecordCategoryEnum


class GetUserRecentSearchModel(BaseModel):
    display_name: str = Field(
        description="The location display name of the recent search.",
    )

    # Individual Location Components
    location_info: GetUserSearchLocationModel = Field(
        description="The location info of the recent search.",
    )

    # Record Types and Categories
    record_types: list[RecordTypesEnum] = Field(
        description="The record types of the recent search.",
    )
    record_categories: list[RecordCategoryEnum] = Field(
        description="The record categories of the recent search.",
    )

    # Search Date
    search_date: datetime = Field(
        description="The date of the recent search.",
    )
