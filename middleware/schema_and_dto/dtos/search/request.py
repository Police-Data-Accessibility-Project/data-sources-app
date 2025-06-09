from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel, model_validator

from middleware.enums import RecordTypes, OutputFormatEnum
from middleware.flask_response_manager import FlaskResponseManager
from utilities.enums import RecordCategories


class SearchRequestsDTO(BaseModel):
    location_id: int
    record_categories: Optional[list[RecordCategories]] = None
    record_types: Optional[list[RecordTypes]] = None
    output_format: Optional[OutputFormatEnum] = None

    @model_validator(mode="after")
    def check_exclusive_fields(self):

        if self.record_categories is not None and self.record_types is not None:
            if self.record_categories == [RecordCategories.ALL]:
                self.record_categories = None
                return

            FlaskResponseManager.abort(
                message="Only one of 'record_categories' or 'record_types' should be provided.",
                code=HTTPStatus.BAD_REQUEST,
            )
            raise ValueError(
                "Only one of 'record_categories' or 'record_types' should be provided, not both."
            )
