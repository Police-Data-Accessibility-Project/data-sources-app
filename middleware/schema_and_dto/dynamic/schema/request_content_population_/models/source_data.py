from pydantic import BaseModel

from middleware.schema_and_dto.dynamic.schema.request_content_population_.models.nested_dto import NestedDTOInfo


class SourceDataInfo(BaseModel):
    data: dict
    nested_dto_info_list: list[NestedDTOInfo]
