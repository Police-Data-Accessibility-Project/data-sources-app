import copy
from dataclasses import dataclass
from typing import Any, Optional, Type, TypeVar, Dict

from marshmallow import Schema, fields
from marshmallow.fields import Field

from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_advanced_schemas import (
    DataSourcesPostSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_base_schemas import (
    DataSourceBaseSchema,
)

from marshmallow import Schema, fields, ValidationError


class FlatSchema(Schema):
    """
    A custom schema class that enforces flatness.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ensure_no_nested_fields()

    def _ensure_no_nested_fields(self):
        for field_name, field_obj in self.fields.items():
            if isinstance(field_obj, fields.Nested):
                raise ValidationError(
                    f"Field '{field_name}' is a nested schema, which is not permitted in FlatSchema."
                )

    # Override the add_field method to enforce flatness
    def add_field(self, name, field_obj):
        if isinstance(field_obj, fields.Nested):
            raise ValidationError(
                f"Cannot add nested schema field '{name}' to FlatSchema."
            )
        super().add_field(name, field_obj)


@dataclass
class FieldPathValueMapping:

    def __init__(
        self,
        field_path,
        field,
        name: str | CSVColumnCondition = CSVColumnCondition.SAME_AS_FIELD,
    ):
        self.field_path = field_path
        self.field = field
        if name == CSVColumnCondition.SAME_AS_FIELD:
            self.name = field_path[-1]
        else:
            self.name = name

    def get_schema_notation(self):
        return ".".join(self.field_path)

    def get_field_name(self):
        return self.field_path[-1]


def extract_specific_metadata(
    schema: Schema, key: str, parent_path: Optional[list[str]] = None
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
            metadata.append(
                FieldPathValueMapping(
                    field_path=current_path, name=field.metadata[key], field=field
                ),
            )

        # Check if the field is a nested schema
        if isinstance(field, fields.Nested) and isinstance(field.schema, Schema):
            # Recursively extract nested schema metadata
            nested_metadata = extract_specific_metadata(field.schema, key, current_path)
            metadata.extend(nested_metadata)

        # Check if the field is a list with a nested schema
        elif isinstance(field, fields.List) and isinstance(field.inner, fields.Nested):
            if isinstance(field.inner.schema, Schema):
                nested_metadata = extract_specific_metadata(
                    field.inner.schema, key, current_path + ["[]"]
                )
                metadata.extend(nested_metadata)

    return metadata


def get_csv_columns_from_schema(schema: Schema) -> list[FieldPathValueMapping]:
    """
    Go through all fields which have `csv_column_name` metadata
    and add their full path to the mapping
    """
    fieldpath_value_mapping = extract_specific_metadata(schema, "csv_column_name")
    return fieldpath_value_mapping


def generate_flat_csv_schema(
    schema: Schema, additional_fields: Optional[Dict[str, Field]] = None
) -> Type[FlatSchema]:
    """
    Dynamically generate flat csv schema from a nested schema
    """
    fpvms = get_csv_columns_from_schema(schema)
    new_fields = {}
    for fpvm in fpvms:
        new_fields[fpvm.name] = copy.copy(fpvm.field)
    if additional_fields is not None:
        new_fields.update(additional_fields)
    NewSchema = type(f"Flat{schema.__class__.__name__}", (FlatSchema,), new_fields)

    return NewSchema


def create_csv_column_to_field_map(
    fpvms: list[FieldPathValueMapping],
) -> dict[str, list[str]]:
    csv_column_to_field_map = {}
    for fpvm in fpvms:
        if fpvm.name is CSVColumnCondition.SAME_AS_FIELD:
            field_name = fpvm.get_field_name()
        else:
            field_name = fpvm.name
        csv_column_to_field_map[field_name] = fpvm.field_path

    return csv_column_to_field_map


if __name__ == "__main__":
    mapping = get_csv_columns_from_schema(schema=DataSourcesPostSchema())
    new_schema = generate_flat_csv_schema(schema=DataSourcesPostSchema())
    print(new_schema)
