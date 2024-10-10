from enum import Enum
from typing import Optional, Type

from marshmallow import Schema

from middleware.primary_resource_logic.data_requests import RelatedSourceByIDSchema, RelatedSourceByIDDTO
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyRequestsBaseSchema, GetManyBaseDTO, \
    GetByIDBaseSchema, GetByIDBaseDTO, EntryCreateUpdateRequestDTO, EntryDataRequestSchema
from middleware.schema_and_dto_logic.custom_types import DTOTypes
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_schemas import AgenciesGetByIDResponseSchema, \
    AgenciesPutSchema, AgenciesPostSchema, AgenciesPostDTO, AgenciesGetManyResponseSchema
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_schemas import GetManyDataRequestsSchema, \
    DataRequestsSchema, DataRequestsPostSchema, GetByIDDataRequestsResponseSchema
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_schemas import DataSourcesGetManySchema, \
    DataSourcesGetByIDSchema, DataSourcesPostSchema, DataSourcesPutSchema, DataSourcesPostDTO
from middleware.schema_and_dto_logic.common_response_schemas import IDAndMessageSchema, MessageSchema
from middleware.schema_and_dto_logic.primary_resource_schemas.github_issue_app_schemas import \
    GithubDataRequestsIssuesPostRequestSchema, GithubDataRequestsIssuesPostResponseSchema, \
    GithubDataRequestsIssuesPostDTO


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
    #region Data Requests
    DATA_REQUESTS_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyRequestsBaseSchema(),
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
                "entry_data.request_urgency",
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
    #endregion
    #region Agencies
    AGENCIES_BY_ID_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        output_schema=AgenciesGetByIDResponseSchema(),
        input_dto_class=GetByIDBaseDTO
    )
    AGENCIES_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyRequestsBaseSchema(),
        output_schema=AgenciesGetManyResponseSchema(),
        input_dto_class=GetManyBaseDTO
    )
    AGENCIES_POST = EndpointSchemaConfig(
        input_schema=AgenciesPostSchema(),
        input_dto_class=AgenciesPostDTO,
        output_schema=IDAndMessageSchema()
    )
    AGENCIES_BY_ID_PUT = EndpointSchemaConfig(
        input_schema=AgenciesPutSchema(),
        output_schema=MessageSchema()
    )
    #endregion
    #region Data Sources
    DATA_SOURCES_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyRequestsBaseSchema(),
        output_schema=DataSourcesGetManySchema(),
        input_dto_class=GetManyBaseDTO
    )
    DATA_SOURCES_GET_BY_ID = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        output_schema=DataSourcesGetByIDSchema(),
        input_dto_class=GetByIDBaseDTO
    )
    DATA_SOURCES_POST = EndpointSchemaConfig(
        input_schema=DataSourcesPostSchema(),
        input_dto_class=DataSourcesPostDTO,
        output_schema=IDAndMessageSchema()
    )
    DATA_SOURCES_PUT = EndpointSchemaConfig(
        input_schema=DataSourcesPutSchema(),
        input_dto_class=EntryDataRequestSchema
    )
    #endregion

    #region Github
    GITHUB_DATA_REQUESTS_ISSUES_POST = EndpointSchemaConfig(
        input_schema=GithubDataRequestsIssuesPostRequestSchema(),
        output_schema=GithubDataRequestsIssuesPostResponseSchema(),
        input_dto_class=GithubDataRequestsIssuesPostDTO
    )
    #endregion


