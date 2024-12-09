from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_csv_to_schema_conversion_logic import (
    generate_flat_csv_schema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_advanced_schemas import (
    AgenciesPostSchema,
    AgenciesPutSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_advanced_schemas import (
    DataSourcesPostSchema,
    DataSourcesPutSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.enums import SourceMappingEnum


class BatchRequestSchema(Schema):

    file = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.FILE,
            "description": "The file to upload",
        },
    )


class BatchPutRequestSchema(BatchRequestSchema):
    id = fields.Integer(
        required=True, metadata=get_json_metadata("The id of the resource to update")
    )


# region Base Schemas
DataSourcesPostRequestFlatBaseSchema = generate_flat_csv_schema(
    schema=DataSourcesPostSchema()
)
DataSourcesPutRequestFlatBaseSchema = generate_flat_csv_schema(
    schema=DataSourcesPutSchema(),
)
AgenciesPostRequestFlatBaseSchema = generate_flat_csv_schema(
    schema=AgenciesPostSchema()
)
AgenciesPutRequestFlatBaseSchema = generate_flat_csv_schema(schema=AgenciesPutSchema())
# endregion


# region RequestSchemas
class DataSourcesPostBatchRequestSchema(
    BatchRequestSchema, DataSourcesPostRequestFlatBaseSchema
):
    pass


class DataSourcesPutBatchRequestSchema(
    BatchPutRequestSchema, DataSourcesPutRequestFlatBaseSchema
):
    pass


class AgenciesPostBatchRequestSchema(
    BatchRequestSchema, AgenciesPostRequestFlatBaseSchema
):
    pass


class AgenciesPutBatchRequestSchema(
    BatchPutRequestSchema, AgenciesPutRequestFlatBaseSchema
):
    pass


# endregion


class BatchPostResponseSchema(MessageSchema):
    ids = fields.List(
        fields.Integer(metadata=get_json_metadata("The ids of the resources created")),
        required=True,
        metadata=get_json_metadata("The ids of the resources created"),
    )
    errors = fields.Dict(
        required=True,
        metadata=get_json_metadata("The errors associated with resources not created"),
    )


class BatchPutResponseSchema(MessageSchema):
    errors = fields.Dict(
        required=True,
        metadata=get_json_metadata("The errors associated with resources not updated"),
    )
