from marshmallow import fields, ValidationError


class DataField(fields.Dict):
    def _deserialize(self, value, attr, data, **kwargs):
        # First call parent deserialization logic
        result = super()._deserialize(value, attr, data, **kwargs)

        # Now check that no values are dictionaries
        for key, val in result.items():
            if isinstance(val, dict):
                raise ValidationError(f"Nested dictionaries not allowed: {key}")

        return result


class EntryDataListField(fields.List):
    def _deserialize(self, value, attr, data, **kwargs):
        # First call parent deserialization logic
        result = super()._deserialize(value, attr, data, **kwargs)

        # Now check that no values are dictionaries
        for entry in result:
            for entry_val in entry:
                if isinstance(entry_val, dict):
                    raise ValidationError(
                        f"Nested dictionaries not allowed: {entry_val} in {entry}"
                    )

        return result
