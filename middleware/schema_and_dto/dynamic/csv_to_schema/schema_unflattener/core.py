from typing import Type

from middleware.schema_and_dto.dynamic.csv_to_schema.core import (
    get_csv_columns_from_schema,
)
from middleware.schema_and_dto.dynamic.csv_to_schema.schema_unflattener.helpers import (
    set_nested_value,
)
from middleware.schema_and_dto.dynamic.csv_to_schema.flat_schema import FlatSchema
from middleware.schema_and_dto.dynamic.schema.request_content_population import (
    get_nested_dto_info_list,
)


class SchemaUnflattener:
    def __init__(self, flat_schema_class: Type[FlatSchema]):
        self.flat_schema_class = flat_schema_class
        self.origin_schema_class = flat_schema_class.origin_schema
        self.origin_schema = self.origin_schema_class()
        self.fpvms = get_csv_columns_from_schema(schema=self.origin_schema)
        self.nested_dto_info_list = get_nested_dto_info_list(schema=self.origin_schema)

    def unflatten(self, flat_data: dict) -> dict:
        data = {}
        for fpvm in self.fpvms:
            if fpvm.name not in flat_data:
                continue
            set_nested_value(
                d=data,
                path=fpvm.field_path,
                value=flat_data[fpvm.name],
            )
        return data
