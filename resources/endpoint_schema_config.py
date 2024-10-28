from enum import Enum
from typing import Optional, Type

from marshmallow import Schema

from middleware.primary_resource_logic.data_requests import (
    RelatedSourceByIDSchema,
    RelatedSourceByIDDTO, DataRequestsPostDTO,
)
from middleware.primary_resource_logic.typeahead_suggestion_logic import TypeaheadLocationsOuterResponseSchema, \
    TypeaheadAgenciesOuterResponseSchema
from middleware.primary_resource_logic.unique_url_checker import UniqueURLCheckerRequestSchema, \
    UniqueURLCheckerResponseOuterSchema, UniqueURLCheckerRequestDTO
from middleware.schema_and_dto_logic.primary_resource_dtos.data_requests_dtos import GetManyDataRequestsRequestsDTO
from middleware.schema_and_dto_logic.primary_resource_schemas.notifications_schemas import NotificationsResponseSchema
from middleware.schema_and_dto_logic.primary_resource_schemas.search_schemas import SearchRequestSchema, \
    GetUserFollowedSearchesSchema, SearchRequests, FollowSearchResponseSchema, SearchResultsInnerSchema, \
    SearchResponseSchema
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
    GetManyBaseDTO,
    GetByIDBaseSchema,
    GetByIDBaseDTO,
    EntryCreateUpdateRequestDTO,
    EntryDataRequestSchema, TypeaheadDTO, TypeaheadQuerySchema,
)
from middleware.schema_and_dto_logic.custom_types import DTOTypes
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_schemas import (
    AgenciesGetByIDResponseSchema,
    AgenciesPutSchema,
    AgenciesPostSchema,
    AgenciesPostDTO,
    AgenciesGetManyResponseSchema, RelatedAgencyByIDSchema, RelatedAgencyByIDDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_schemas import (
    GetManyDataRequestsResponseSchema,
    DataRequestsSchema,
    DataRequestsPostSchema,
    GetByIDDataRequestsResponseSchema, GetManyDataRequestsRequestsSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_schemas import (
    DataSourcesGetManySchema,
    DataSourcesGetByIDSchema,
    DataSourcesPostSchema,
    DataSourcesPutSchema,
    DataSourcesPostDTO, DataSourcesGetManyRequestSchema,
)
from middleware.schema_and_dto_logic.common_response_schemas import (
    IDAndMessageSchema,
    MessageSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.github_issue_app_schemas import (
    GithubDataRequestsIssuesPostRequestSchema,
    GithubDataRequestsIssuesPostResponseSchema,
    GithubDataRequestsIssuesPostDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.user_profile_schemas import \
    GetUserRecentSearchesOuterSchema


class EndpointSchemaConfig:
    def __init__(
        self,
        input_schema: Optional[Schema] = None,
        output_schema: Optional[Schema] = None,
        input_dto_class: Optional[Type[DTOTypes]] = None,
    ):
        """

        :param input_schema: Describes the schema to be input on a request
        :param output_schema: Describes the schema to be output on a successful request
        :param input_dto_class: Describes the DTO which will be populated based on the input schema.
        """
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.input_dto_class = input_dto_class

    def get_schema_populate_parameters(self) -> SchemaPopulateParameters:
        return SchemaPopulateParameters(
            schema=self.input_schema, dto_class=self.input_dto_class
        )


class SchemaConfigs(Enum):
    # region Data Requests
    DATA_REQUESTS_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyDataRequestsRequestsSchema(),
        output_schema=GetManyDataRequestsResponseSchema(),
        input_dto_class=GetManyDataRequestsRequestsDTO,
    )
    DATA_REQUESTS_BY_ID_GET = EndpointSchemaConfig(
        input_schema=None, output_schema=GetByIDDataRequestsResponseSchema()
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
        output_schema=None,
    )
    DATA_REQUESTS_POST = EndpointSchemaConfig(
        input_schema=DataRequestsPostSchema(),
        input_dto_class=DataRequestsPostDTO,
        output_schema=IDAndMessageSchema(),
    )
    DATA_REQUESTS_RELATED_SOURCES_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        output_schema=DataSourcesGetManySchema(exclude=["data.agencies"], partial=True),
        input_dto_class=GetByIDBaseDTO,
    )
    DATA_REQUESTS_RELATED_SOURCES_POST = EndpointSchemaConfig(
        input_schema=RelatedSourceByIDSchema(), input_dto_class=RelatedSourceByIDDTO
    )
    DATA_REQUESTS_RELATED_SOURCES_DELETE = EndpointSchemaConfig(
        input_schema=RelatedSourceByIDSchema(), input_dto_class=RelatedSourceByIDDTO
    )
    # endregion
    # region Agencies
    AGENCIES_BY_ID_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        output_schema=AgenciesGetByIDResponseSchema(),
        input_dto_class=GetByIDBaseDTO,
    )
    AGENCIES_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyRequestsBaseSchema(),
        output_schema=AgenciesGetManyResponseSchema(),
        input_dto_class=GetManyBaseDTO,
    )
    AGENCIES_POST = EndpointSchemaConfig(
        input_schema=AgenciesPostSchema(),
        input_dto_class=AgenciesPostDTO,
        output_schema=IDAndMessageSchema(),
    )
    AGENCIES_BY_ID_PUT = EndpointSchemaConfig(
        input_schema=AgenciesPutSchema(), output_schema=MessageSchema()
    )
    # endregion
    # region Data Sources
    DATA_SOURCES_GET_MANY = EndpointSchemaConfig(
        input_schema=DataSourcesGetManyRequestSchema(),
        output_schema=DataSourcesGetManySchema(),
        input_dto_class=GetManyBaseDTO,
    )
    DATA_SOURCES_GET_BY_ID = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        output_schema=DataSourcesGetByIDSchema(),
        input_dto_class=GetByIDBaseDTO,
    )
    DATA_SOURCES_POST = EndpointSchemaConfig(
        input_schema=DataSourcesPostSchema(),
        input_dto_class=DataSourcesPostDTO,
        output_schema=IDAndMessageSchema(),
    )
    DATA_SOURCES_PUT = EndpointSchemaConfig(
        input_schema=DataSourcesPutSchema(), input_dto_class=EntryDataRequestSchema
    )
    DATA_SOURCES_RELATED_AGENCIES_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        output_schema=AgenciesGetManyResponseSchema(),
        input_dto_class=GetByIDBaseDTO
    )
    DATA_SOURCES_RELATED_AGENCIES_POST = EndpointSchemaConfig(
        input_schema=RelatedAgencyByIDSchema(),
        input_dto_class=RelatedAgencyByIDDTO
    )
    DATA_SOURCES_RELATED_AGENCIES_DELETE = EndpointSchemaConfig(
        input_schema=RelatedAgencyByIDSchema(),
        input_dto_class=RelatedAgencyByIDDTO
    )
    # endregion

    # region Github
    GITHUB_DATA_REQUESTS_ISSUES_POST = EndpointSchemaConfig(
        input_schema=GithubDataRequestsIssuesPostRequestSchema(),
        output_schema=GithubDataRequestsIssuesPostResponseSchema(),
        input_dto_class=GithubDataRequestsIssuesPostDTO,
    )
    GITHUB_DATA_REQUESTS_SYNCHRONIZE_POST = EndpointSchemaConfig(
        input_schema=None, output_schema=MessageSchema(), input_dto_class=None
    )
    # endregion
    #region Search
    SEARCH_LOCATION_AND_RECORD_TYPE_GET = EndpointSchemaConfig(
        input_schema=SearchRequestSchema(),
        output_schema=SearchResponseSchema(),
        input_dto_class=SearchRequests
    )
    SEARCH_FOLLOW_GET = EndpointSchemaConfig(
        output_schema=GetUserFollowedSearchesSchema(),
    )
    SEARCH_FOLLOW_POST = EndpointSchemaConfig(
        input_schema=SearchRequestSchema(
            exclude=["record_categories"],
        ),
        input_dto_class=SearchRequests,
        output_schema=MessageSchema(),
    )
    SEARCH_FOLLOW_DELETE = EndpointSchemaConfig(
        input_schema=SearchRequestSchema(
            exclude=["record_categories"],
        ),
        input_dto_class=SearchRequests,
        output_schema=MessageSchema(),
    )

    #endregion
    #region Typeahead
    TYPEAHEAD_LOCATIONS = EndpointSchemaConfig(
        input_schema=TypeaheadQuerySchema(),
        output_schema=TypeaheadLocationsOuterResponseSchema(),
        input_dto_class=TypeaheadDTO
    )
    TYPEAHEAD_AGENCIES = EndpointSchemaConfig(
        input_schema=TypeaheadQuerySchema(),
        output_schema=TypeaheadAgenciesOuterResponseSchema(),
        input_dto_class=TypeaheadDTO
    )
    #endregion
    #region Checker
    CHECKER_GET = EndpointSchemaConfig(
        input_schema=UniqueURLCheckerRequestSchema(),
        output_schema=UniqueURLCheckerResponseOuterSchema(),
        input_dto_class=UniqueURLCheckerRequestDTO
    )
    #endregion
    #region Notifications
    NOTIFICATIONS_POST = EndpointSchemaConfig(
        output_schema=NotificationsResponseSchema(),
    )
    #region User Profile
    USER_PROFILE_RECENT_SEARCHES = EndpointSchemaConfig(
        output_schema=GetUserRecentSearchesOuterSchema(exclude=['message']),
    )
    #endregion
