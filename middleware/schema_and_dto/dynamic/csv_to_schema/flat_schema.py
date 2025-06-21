from typing import Type

from marshmallow import Schema, fields, ValidationError


class FlatSchema(Schema):
    """
    A custom schema class that enforces flatness.
    """

    origin_schema: Type[Schema]

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
        super().add_field(  # pyright: ignore[reportAttributeAccessIssue]
            name, field_obj
        )
