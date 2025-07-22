from marshmallow import Schema, fields

from middleware.schema_and_dto.dtos.data_requests.put import DataRequestsPutDTO
from endpoints.instantiations.data_requests_._shared.schemas.base import (
    DataRequestsSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class DataRequestsPutSchema(Schema):
    entry_data = fields.Nested(
        nested=DataRequestsSchema(
            exclude=[
                "id",
                "date_created",
                "date_status_last_changed",
                "creator_user_id",
            ],
            partial=True,
        ),
        metadata=get_json_metadata(
            "The information about the data request to be updated",
            nested_dto_class=DataRequestsPutDTO,
        ),
        required=True,
    )
