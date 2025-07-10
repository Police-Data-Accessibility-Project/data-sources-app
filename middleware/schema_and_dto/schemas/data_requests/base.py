from marshmallow import Schema, fields, validate

from db.enums import RequestStatus, RequestUrgency
from endpoints.instantiations.data_requests_._shared.dtos.base import DataRequestsBaseDTO
from middleware.enums import RecordTypes
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.util import get_json_metadata

DataRequestsSchema = pydantic_to_marshmallow(DataRequestsBaseDTO)
#
# class DataRequestsSchema(Schema):
#     """
#     Reflects the columns in the `data_requests` database table
#     """
#
#     id = fields.Integer(
#         metadata=get_json_metadata("The ID of the data request"),
#     )
#     title = fields.String(
#         metadata=get_json_metadata("The title of the data request"),
#         required=True,
#         validate=validate.Length(min=1, max=255),
#     )
#     submission_notes = fields.String(
#         allow_none=True,
#         metadata=get_json_metadata(
#             "Optional notes provided by the submitter during the request submission."
#         ),
#     )
#     request_status = fields.Enum(
#         enum=RequestStatus,
#         by_value=fields.Str,
#         metadata=get_json_metadata(
#             "The current status of the data request. Editable only by admins."
#         ),
#     )
#
#     archive_reason = fields.String(
#         allow_none=True,
#         metadata=get_json_metadata(
#             "If applicable, the reason for archiving the data request. Viewable only by owners and admins. Editable only by admins."
#         ),
#     )
#     date_created = fields.DateTime(
#         format="iso", metadata=get_json_metadata("When the data request was created.")
#     )
#     date_status_last_changed = fields.DateTime(
#         format="iso",
#         metadata=get_json_metadata(
#             "The date and time when the status of the request was last changed."
#         ),
#     )
#     creator_user_id = fields.Integer(
#         metadata=get_json_metadata("The ID of the user who created the data request.")
#     )
#     github_issue_url = fields.String(
#         allow_none=True,
#         metadata=get_json_metadata(
#             "If applicable, the URL to the issue on Github. Editable only by admins."
#         ),
#     )
#     github_issue_number = fields.Integer(
#         allow_none=True,
#         metadata=get_json_metadata(
#             "If applicable, the number of the issue on Github. Editable only by admins."
#         ),
#     )
#     internal_notes = fields.String(
#         allow_none=True,
#         metadata=get_json_metadata(
#             "Internal notes by PDAP staff about the request. Viewable and editable only by admins."
#         ),
#     )
#     record_types_required = fields.List(
#         fields.Enum(
#             enum=RecordTypes,
#             by_value=fields.Str,
#             metadata=get_json_metadata(
#                 "The record types associated with the data request. Editable only by admins."
#             ),
#         ),
#         allow_none=True,
#         metadata=get_json_metadata(
#             "Multi-select of record types from record_types taxonomy. Editable only by admins."
#         ),
#     )
#     pdap_response = fields.String(
#         allow_none=True,
#         metadata=get_json_metadata(
#             "Public notes by PDAP about the request. Editable only by admins."
#         ),
#     )
#     coverage_range = fields.Str(
#         allow_none=True,
#         metadata=get_json_metadata(
#             "The date range covered by the request, if applicable."
#         ),
#     )
#     data_requirements = fields.String(
#         allow_none=True,
#         metadata=get_json_metadata(
#             "Detailed requirements for the data being requested."
#         ),
#     )
#     request_urgency = fields.Enum(
#         enum=RequestUrgency,
#         by_value=fields.Str,
#         metadata=get_json_metadata("The urgency of the request."),
#     )
