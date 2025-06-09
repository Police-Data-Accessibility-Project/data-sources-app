from marshmallow import fields, pre_load

from db.enums import RequestStatus
from middleware.schema_and_dto_logic.dtos.common.base import GetManyRequestsBaseSchema
from middleware.schema_and_dto_logic.util import get_query_metadata


class GetManyDataRequestsRequestsSchema(GetManyRequestsBaseSchema):
    request_statuses = fields.List(
        fields.Enum(
            enum=RequestStatus,
            by_value=fields.Str,
            allow_none=True,
            metadata=get_query_metadata("The status of the requests to return."),
        ),
        metadata=get_query_metadata("The status of the requests to return."),
    )

    @pre_load
    def listify_request_statuses(self, in_data, **kwargs):
        request_statuses = in_data.get("request_statuses", None)
        if request_statuses is None:
            return in_data
        in_data["request_statuses"] = request_statuses.split(",")

        return in_data
