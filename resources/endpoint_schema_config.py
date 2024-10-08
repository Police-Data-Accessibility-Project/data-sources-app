from enum import Enum
from typing import Optional, Type

from marshmallow import Schema

from middleware.primary_resource_logic.data_requests import RelatedSourceByIDSchema, RelatedSourceByIDDTO
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseSchema, GetManyBaseDTO, \
    GetByIDBaseSchema, GetByIDBaseDTO
from middleware.schema_and_dto_logic.custom_types import DTOTypes
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_schemas import GetManyDataRequestsSchema, \
    DataRequestsSchema, DataRequestsPostSchema, GetByIDDataRequestsResponseSchema
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_schemas import DataSourcesGetManySchema
from middleware.schema_and_dto_logic.common_response_schemas import IDAndMessageSchema


class EndpointSchemaConfig:
    def __init__(
            self,
            input_schema: Optional[Schema] = None,
            output_schema: Optional[Schema] = None,
            input_dto_class: Optional[Type[DTOTypes]] = None,
    ):
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.input_dto_class = input_dto_class

    def get_schema_populate_parameters(self) -> SchemaPopulateParameters:
        return SchemaPopulateParameters(
            schema=self.input_schema,
            dto_class=self.input_dto_class
        )


class SchemaConfigs(Enum):
    DATA_REQUESTS_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyBaseSchema(),
        output_schema=GetManyDataRequestsSchema(),
        input_dto_class=GetManyBaseDTO
    )
    DATA_REQUESTS_BY_ID_GET = EndpointSchemaConfig(
        input_schema=None,
        output_schema=GetByIDDataRequestsResponseSchema()
    )
    DATA_REQUESTS_BY_ID_PUT = EndpointSchemaConfig(
        input_schema=DataRequestsSchema(
            exclude=[
                "id",
                "date_created",
                "date_status_last_changed",
                "creator_user_id",
            ]
        ),
        output_schema=None
    )
    DATA_REQUESTS_POST = EndpointSchemaConfig(
        input_schema=DataRequestsPostSchema(
            only=[
                "entry_data.submission_notes",
                "entry_data.location_described_submitted",
                "entry_data.coverage_range",
                "entry_data.data_requirements",
            ]
        ),
        output_schema=IDAndMessageSchema()
    )
    DATA_REQUESTS_RELATED_SOURCES_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        output_schema=DataSourcesGetManySchema(
            exclude=["data.agencies"],
            partial=True
        ),
        input_dto_class=GetByIDBaseDTO
    )
    DATA_REQUESTS_RELATED_SOURCES_POST = EndpointSchemaConfig(
        input_schema=RelatedSourceByIDSchema(),
        input_dto_class=RelatedSourceByIDDTO
    )
    DATA_REQUESTS_RELATED_SOURCES_DELETE = EndpointSchemaConfig(
        input_schema=RelatedSourceByIDSchema(),
        input_dto_class=RelatedSourceByIDDTO
    )
