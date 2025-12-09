from pydantic import BaseModel

from middleware.enums import RecordTypesEnum
from utilities.enums import RecordCategoryEnum


class RecordTypeMapping(BaseModel):
    record_type: RecordTypesEnum
    record_type_id: int
    record_category: RecordCategoryEnum
    record_category_id: int
