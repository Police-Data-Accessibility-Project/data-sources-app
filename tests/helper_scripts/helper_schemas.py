"""
These are schemas which are used for validating the input and/or output of tests
But which are not used in the app code itself
"""
from marshmallow import Schema, fields

from database_client.enums import EntityType


class TestGetPendingNotificationsOutputSchema(Schema):
    user_id = fields.Int()
    email = fields.Str()
    event_type = fields.Str()
    entity_id = fields.Int()
    entity_type = fields.Enum(
        enum=EntityType,
        by_value=fields.Str
    )
    entity_name = fields.Str()