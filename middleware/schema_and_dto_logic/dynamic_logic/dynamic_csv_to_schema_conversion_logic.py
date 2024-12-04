from dataclasses import dataclass
from typing import Any, Optional

from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_advanced_schemas import DataSourcesPostSchema
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_base_schemas import DataSourceBaseSchema

@dataclass
class FieldPathValueMapping:
    field_path: list[str]
    value: Any

    def get_schema_notation(self):
        return ".".join(self.field_path)

    def get_field_name(self):
        return self.field_path[-1]


def extract_specific_metadata(
        schema: Schema,
        key: str,
        parent_path: Optional[list[str]] = None
) -> list[FieldPathValueMapping]:
    """
    Recursive function to traverse schema for specific metadata key
    """
    if parent_path is None:
        parent_path = []

    metadata = []
    for field_name, field in schema.fields.items():
        # Construct the path to the field
        current_path = parent_path + [field_name]

        # Check if the key exists in the field's metadata
        if key in field.metadata:
            metadata.append(FieldPathValueMapping(field_path=current_path, value=field.metadata[key]))

        # Check if the field is a nested schema
        if isinstance(field, fields.Nested) and isinstance(field.schema, Schema):
            # Recursively extract nested schema metadata
            nested_metadata = extract_specific_metadata(field.schema, key, current_path)
            metadata.extend(nested_metadata)

        # Check if the field is a list with a nested schema
        elif isinstance(field, fields.List) and isinstance(field.inner, fields.Nested):
            if isinstance(field.inner.schema, Schema):
                nested_metadata = extract_specific_metadata(field.inner.schema, key, current_path + ["[]"])
                metadata.extend(nested_metadata)

    return metadata


def get_csv_columns_from_schema(schema: Schema) -> list[FieldPathValueMapping]:
    """
    Go through all fields which have `csv_column_name` metadata
    and add their full path to the mapping
    """
    fieldpath_value_mapping = extract_specific_metadata(
        schema,
        "csv_column_name"
    )
    return fieldpath_value_mapping

def create_csv_column_to_field_map(
        fpvms: list[FieldPathValueMapping]
) -> dict[str, list[str]]:
    csv_column_to_field_map = {}
    for fpvm in fpvms:
        if fpvm.value is CSVColumnCondition.SAME_AS_FIELD:
            field_name = fpvm.get_field_name()
        else:
            field_name = fpvm.value
        csv_column_to_field_map[field_name] = fpvm.field_path

    return csv_column_to_field_map

if __name__ == "__main__":
    print(get_csv_columns_from_schema(
        schema=DataSourcesPostSchema()
    ))