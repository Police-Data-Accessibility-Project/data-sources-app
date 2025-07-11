from marshmallow import Schema

from middleware.schema_and_dto.schemas.common.custom_fields import DataField
from utilities.enums import SourceMappingEnum


class EntryDataRequestSchema(Schema):
    entry_data = DataField(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The entry data field for adding and updating entries",
        },
    )
