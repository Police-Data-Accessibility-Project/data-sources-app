from marshmallow import fields

from middleware.schema_and_dto.util import get_json_metadata


def get_change_field(field_name):
    return fields.Int(
        metadata=get_json_metadata(
            f"The change in {field_name} since the last notification"
        )
    )


def get_count_field(field_name):
    return fields.Int(metadata=get_json_metadata(f"The number of {field_name}"))
