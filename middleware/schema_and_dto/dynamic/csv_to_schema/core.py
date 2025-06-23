import copy
from typing import Optional, Type, Dict

from marshmallow import Schema, fields
from marshmallow.fields import Field

from middleware.schema_and_dto.dynamic.csv_to_schema.field_path_value_mapping import (
    FieldPathValueMapping,
)
from middleware.schema_and_dto.dynamic.csv_to_schema.flat_schema import FlatSchema


def extract_field_path_value_mapping(
    schema: Schema, key: str, parent_path: Optional[list[str]] = None
) -> list[FieldPathValueMapping]:
    """
    Recursive function to traverse schema for specific metadata key

    :param schema: The schema to extract metadata from
    :param key: The key to extract from the metadata
    :param parent_path: The path to the parent field
    :return: A list of field path value mappings
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
            nested_metadata = extract_field_path_value_mapping(
                field.schema, key, current_path
            )
            metadata.extend(nested_metadata)

        # Check if the field is a list with a nested schema
        elif isinstance(field, fields.List) and isinstance(field.inner, fields.Nested):
            if isinstance(field.inner.schema, Schema):
                nested_metadata = extract_field_path_value_mapping(
                    field.inner.schema, key, current_path + ["[]"]
                )
                metadata.extend(nested_metadata)

    return metadata


def get_csv_columns_from_schema(schema: Schema) -> list[FieldPathValueMapping]:
    """
    Go through all fields which have `csv_column_name` metadata
    and add their full path to the mapping
    """
    fieldpath_value_mapping = extract_field_path_value_mapping(
        schema, "csv_column_name"
    )
    return fieldpath_value_mapping


def generate_flat_csv_schema(
    schema: Schema, additional_fields: Optional[Dict[str, Field]] = None
) -> Type[FlatSchema]:
    """
    Dynamically generate flat csv schema from a nested schema
    """
    fpvms = get_csv_columns_from_schema(schema)
    new_fields = {}
    schema_class = schema.__class__
    new_fields["origin_schema"] = schema_class
    for fpvm in fpvms:
        new_fields[fpvm.name] = copy.copy(fpvm.field)
    if additional_fields is not None:
        new_fields.update(additional_fields)
    NewSchema = type(f"Flat{schema_class.__name__}", (FlatSchema,), new_fields)

    return NewSchema
