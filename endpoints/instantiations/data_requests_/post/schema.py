from marshmallow import Schema, fields, post_load

from endpoints.instantiations.data_requests_._shared.schemas.base import DataRequestsSchema
from endpoints.instantiations.data_requests_.post.dto import RequestInfoPostDTO, DataRequestsPostDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.util import get_json_metadata


DataRequestsPostSchema = pydantic_to_marshmallow(DataRequestsPostDTO)
#
# class DataRequestsPostSchema(Schema):
#     request_info = fields.Nested(
#         nested=DataRequestsSchema(
#             only=[
#                 "title",
#                 "submission_notes",
#                 "data_requirements",
#                 "request_urgency",
#                 "coverage_range",
#             ]
#         ),
#         metadata=get_json_metadata(
#             "The information about the data request to be created",
#             nested_dto_class=RequestInfoPostDTO,
#         ),
#         required=True,
#     )
#     location_ids = fields.List(
#         fields.Integer(
#             metadata=get_json_metadata(
#                 "The location ids associated with the data request",
#             ),
#         ),
#         required=False,
#         allow_none=True,
#         metadata=get_json_metadata("The location ids associated with the data request"),
#     )
#
#     @post_load
#     def location_ids_convert_empty_list_to_none(self, in_data, **kwargs):
#         location_ids = in_data.get("location_ids", None)
#         if location_ids == []:
#             in_data["location_ids"] = None
#         return in_data
