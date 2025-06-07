from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.dtos.data_sources_dtos import (
    DataSourceEntryDataPostDTO,
)
from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.schemas.data_sources.expanded import (
    DataSourceExpandedSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class DataSourcesPostSchema(Schema):
    entry_data = fields.Nested(
        nested=DataSourceExpandedSchema(
            exclude=[
                "id",
                "updated_at",
                "created_at",
                "record_type_id",
                "approval_status_updated_at",
                "broken_source_url_as_of",
                "last_approval_editor",
                "last_approval_editor_old",
            ],
            partial=True,
        ),
        required=True,
        metadata=get_json_metadata(
            description="The data source to be created",
            nested_dto_class=DataSourceEntryDataPostDTO,
        ),
    )
    linked_agency_ids = fields.List(
        fields.Integer(
            allow_none=True,
            metadata=get_json_metadata(
                "The agency ids associated with the data source.",
                csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
            ),
        ),
        metadata=get_json_metadata(
            "The agency ids associated with the data source.",
            csv_column_name=CSVColumnCondition.SAME_AS_FIELD,
        ),
    )
