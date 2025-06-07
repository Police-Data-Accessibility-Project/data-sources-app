from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.dtos.data_sources_dtos import (
    DataSourceEntryDataPutDTO,
)
from middleware.schema_and_dto_logic.schemas.data_sources.expanded import (
    DataSourceExpandedSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class DataSourcesPutSchema(Schema):
    entry_data = fields.Nested(
        nested=DataSourceExpandedSchema(
            exclude=[
                "id",
                "updated_at",
                "created_at",
                "record_type_id",
                "data_source_request",
                "approval_status_updated_at",
                "broken_source_url_as_of",
                "last_approval_editor",
                "last_approval_editor_old",
            ]
        ),
        required=True,
        metadata=get_json_metadata(
            "The data source to be updated",
            nested_dto_class=DataSourceEntryDataPutDTO,
        ),
    )
