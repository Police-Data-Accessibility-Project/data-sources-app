from enum import Enum
from http import HTTPStatus
from typing import Optional, Type

from marshmallow import Schema

from middleware.primary_resource_logic.callback_primary_logic import (
    LinkToGithubRequestDTO,
)
from middleware.primary_resource_logic.data_requests import (
    RelatedSourceByIDSchema,
    RelatedSourceByIDDTO,
    DataRequestsPostDTO,
    RelatedLocationsByIDDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.refresh_session_schemas import (
    RefreshSessionRequestSchema,
    RefreshSessionRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.typeahead_suggestion_schemas import (
    TypeaheadAgenciesOuterResponseSchema,
    TypeaheadLocationsOuterResponseSchema,
    TypeaheadLocationsResponseSchema,
)
from middleware.primary_resource_logic.unique_url_checker import (
    UniqueURLCheckerRequestSchema,
    UniqueURLCheckerResponseOuterSchema,
    UniqueURLCheckerRequestDTO,
)
from middleware.primary_resource_logic.user_queries import (
    UserRequestSchema,
    UserRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.auth_schemas import (
    LoginResponseSchema,
    LinkToGithubRequestSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.data_requests_dtos import (
    GetManyDataRequestsRequestsDTO,
    DataRequestsPutOuterDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.notifications_schemas import (
    NotificationsResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.search_schemas import (
    SearchRequestSchema,
    GetUserFollowedSearchesSchema,
    SearchRequests,
    SearchResponseSchema,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
    GetManyBaseDTO,
    GetByIDBaseSchema,
    GetByIDBaseDTO,
    EntryDataRequestSchema,
    TypeaheadDTO,
    TypeaheadQuerySchema,
    LocationInfoExpandedSchema,
    EntryCreateUpdateRequestDTO,
)
from middleware.schema_and_dto_logic.custom_types import DTOTypes
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_schemas import (
    AgenciesGetByIDResponseSchema,
    AgenciesPutSchema,
    AgenciesPostSchema,
    AgenciesPostDTO,
    AgenciesGetManyResponseSchema,
    RelatedAgencyByIDSchema,
    RelatedAgencyByIDDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_schemas import (
    GetManyDataRequestsResponseSchema,
    DataRequestsSchema,
    DataRequestsPostSchema,
    GetByIDDataRequestsResponseSchema,
    GetManyDataRequestsRequestsSchema,
    DataRequestsRelatedLocationAddRemoveSchema,
    GetManyDataRequestsRelatedLocationsSchema,
    DataRequestsPutSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_schemas import (
    DataSourcesGetManySchema,
    DataSourcesGetByIDSchema,
    DataSourcesPostSchema,
    DataSourcesPutSchema,
    DataSourcesPostDTO,
    DataSourcesGetManyRequestSchema,
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
from middleware.schema_and_dto_logic.primary_resource_schemas.user_profile_schemas import (
    GetUserRecentSearchesOuterSchema,
)


class OutputSchemaManager:
    def __init__(self, output_schemas: dict[HTTPStatus, Schema]):
        self.output_schemas = output_schemas

    def get_output_schema(self, status_code: HTTPStatus) -> Schema:
        return self.output_schemas.get(status_code, None)

    def get_output_schemas(self) -> dict[HTTPStatus, Schema]:
        return self.output_schemas


class EndpointSchemaConfig:
    def __init__(
        self,
        input_schema: Optional[Schema] = None,
        primary_output_schema: Optional[Schema] = None,
        input_dto_class: Optional[Type[DTOTypes]] = None,
        additional_output_schemas: Optional[dict[HTTPStatus, Schema]] = None,
    ):
        """

        :param input_schema: Describes the schema to be input on a request
        :param primary_output_schema: Describes the schema to be output on a successful request
        :param input_dto_class: Describes the DTO which will be populated based on the input schema.
        """
        self.input_schema = input_schema
        self.primary_output_schema = primary_output_schema
        self.input_dto_class = input_dto_class
        all_output_schemas = {}
        if primary_output_schema is not None:
            all_output_schemas[HTTPStatus.OK] = primary_output_schema
        if additional_output_schemas is not None:
            all_output_schemas.update(additional_output_schemas)
        self.output_schema_manager = OutputSchemaManager(
            output_schemas=all_output_schemas
        )

    def get_schema_populate_parameters(self) -> SchemaPopulateParameters:
        return SchemaPopulateParameters(
            schema=self.input_schema, dto_class=self.input_dto_class
        )


class SchemaConfigs(Enum):
    # region Data Requests
    DATA_REQUESTS_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyDataRequestsRequestsSchema(),
        primary_output_schema=GetManyDataRequestsResponseSchema(),
        input_dto_class=GetManyDataRequestsRequestsDTO,
    )
    DATA_REQUESTS_BY_ID_GET = EndpointSchemaConfig(
        input_schema=None, primary_output_schema=GetByIDDataRequestsResponseSchema()
    )
    DATA_REQUESTS_BY_ID_PUT = EndpointSchemaConfig(
        input_schema=DataRequestsPutSchema(),
        input_dto_class=DataRequestsPutOuterDTO,
        primary_output_schema=MessageSchema(),
    )
    DATA_REQUESTS_POST = EndpointSchemaConfig(
        input_schema=DataRequestsPostSchema(),
        input_dto_class=DataRequestsPostDTO,
        primary_output_schema=IDAndMessageSchema(),
    )
    DATA_REQUESTS_RELATED_SOURCES_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        primary_output_schema=DataSourcesGetManySchema(
            exclude=["data.agencies"], partial=True
        ),
        input_dto_class=GetByIDBaseDTO,
    )
    DATA_REQUESTS_RELATED_SOURCES_POST = EndpointSchemaConfig(
        input_schema=RelatedSourceByIDSchema(), input_dto_class=RelatedSourceByIDDTO
    )
    DATA_REQUESTS_RELATED_SOURCES_DELETE = EndpointSchemaConfig(
        input_schema=RelatedSourceByIDSchema(), input_dto_class=RelatedSourceByIDDTO
    )
    DATA_REQUESTS_RELATED_LOCATIONS_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        input_dto_class=GetByIDBaseDTO,
        primary_output_schema=GetManyDataRequestsRelatedLocationsSchema(),
    )
    DATA_REQUESTS_RELATED_LOCATIONS_POST = EndpointSchemaConfig(
        input_schema=DataRequestsRelatedLocationAddRemoveSchema(),
        input_dto_class=RelatedLocationsByIDDTO,
        primary_output_schema=MessageSchema(),
    )
    DATA_REQUESTS_RELATED_LOCATIONS_DELETE = EndpointSchemaConfig(
        input_schema=DataRequestsRelatedLocationAddRemoveSchema(),
        input_dto_class=RelatedLocationsByIDDTO,
        primary_output_schema=MessageSchema(),
    )
    # endregion
    # region Agencies
    AGENCIES_BY_ID_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        primary_output_schema=AgenciesGetByIDResponseSchema(),
        input_dto_class=GetByIDBaseDTO,
    )
    AGENCIES_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyRequestsBaseSchema(),
        primary_output_schema=AgenciesGetManyResponseSchema(),
        input_dto_class=GetManyBaseDTO,
    )
    AGENCIES_POST = EndpointSchemaConfig(
        input_schema=AgenciesPostSchema(),
        input_dto_class=AgenciesPostDTO,
        primary_output_schema=IDAndMessageSchema(),
    )
    AGENCIES_BY_ID_PUT = EndpointSchemaConfig(
        input_schema=AgenciesPutSchema(), primary_output_schema=MessageSchema()
    )
    # endregion
    # region Data Sources
    DATA_SOURCES_GET_MANY = EndpointSchemaConfig(
        input_schema=DataSourcesGetManyRequestSchema(),
        primary_output_schema=DataSourcesGetManySchema(),
        input_dto_class=GetManyBaseDTO,
    )
    DATA_SOURCES_GET_BY_ID = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        primary_output_schema=DataSourcesGetByIDSchema(),
        input_dto_class=GetByIDBaseDTO,
    )
    DATA_SOURCES_POST = EndpointSchemaConfig(
        input_schema=DataSourcesPostSchema(),
        input_dto_class=DataSourcesPostDTO,
        primary_output_schema=IDAndMessageSchema(),
    )
    DATA_SOURCES_PUT = EndpointSchemaConfig(
        input_schema=DataSourcesPutSchema(), input_dto_class=EntryDataRequestSchema
    )
    DATA_SOURCES_RELATED_AGENCIES_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        primary_output_schema=AgenciesGetManyResponseSchema(),
        input_dto_class=GetByIDBaseDTO,
    )
    DATA_SOURCES_RELATED_AGENCIES_POST = EndpointSchemaConfig(
        input_schema=RelatedAgencyByIDSchema(), input_dto_class=RelatedAgencyByIDDTO
    )
    DATA_SOURCES_RELATED_AGENCIES_DELETE = EndpointSchemaConfig(
        input_schema=RelatedAgencyByIDSchema(), input_dto_class=RelatedAgencyByIDDTO
    )
    # endregion

    # region Github
    GITHUB_DATA_REQUESTS_ISSUES_POST = EndpointSchemaConfig(
        input_schema=GithubDataRequestsIssuesPostRequestSchema(),
        primary_output_schema=GithubDataRequestsIssuesPostResponseSchema(),
        input_dto_class=GithubDataRequestsIssuesPostDTO,
    )
    GITHUB_DATA_REQUESTS_SYNCHRONIZE_POST = EndpointSchemaConfig(
        input_schema=None, primary_output_schema=MessageSchema(), input_dto_class=None
    )
    # endregion
    # region Search
    SEARCH_LOCATION_AND_RECORD_TYPE_GET = EndpointSchemaConfig(
        input_schema=SearchRequestSchema(),
        primary_output_schema=SearchResponseSchema(),
        input_dto_class=SearchRequests,
    )
    SEARCH_FOLLOW_GET = EndpointSchemaConfig(
        primary_output_schema=GetUserFollowedSearchesSchema(),
    )
    SEARCH_FOLLOW_POST = EndpointSchemaConfig(
        input_schema=SearchRequestSchema(
            exclude=["record_categories"],
        ),
        input_dto_class=SearchRequests,
        primary_output_schema=MessageSchema(),
    )
    SEARCH_FOLLOW_DELETE = EndpointSchemaConfig(
        input_schema=SearchRequestSchema(
            exclude=["record_categories"],
        ),
        input_dto_class=SearchRequests,
        primary_output_schema=MessageSchema(),
    )

    # endregion
    # region Typeahead
    TYPEAHEAD_LOCATIONS = EndpointSchemaConfig(
        input_schema=TypeaheadQuerySchema(),
        primary_output_schema=TypeaheadLocationsOuterResponseSchema(),
        input_dto_class=TypeaheadDTO,
    )
    TYPEAHEAD_AGENCIES = EndpointSchemaConfig(
        input_schema=TypeaheadQuerySchema(),
        primary_output_schema=TypeaheadAgenciesOuterResponseSchema(),
        input_dto_class=TypeaheadDTO,
    )
    # endregion
    # region Checker
    CHECKER_GET = EndpointSchemaConfig(
        input_schema=UniqueURLCheckerRequestSchema(),
        primary_output_schema=UniqueURLCheckerResponseOuterSchema(),
        input_dto_class=UniqueURLCheckerRequestDTO,
    )
    # endregion
    # region Notifications
    NOTIFICATIONS_POST = EndpointSchemaConfig(
        primary_output_schema=NotificationsResponseSchema(),
    )
    # region User Profile
    USER_PROFILE_RECENT_SEARCHES = EndpointSchemaConfig(
        primary_output_schema=GetUserRecentSearchesOuterSchema(exclude=["message"]),
    )
    # endregion
    # region Auth
    LOGIN_POST = EndpointSchemaConfig(
        input_schema=UserRequestSchema(),
        primary_output_schema=LoginResponseSchema(),
        input_dto_class=UserRequestDTO,
    )
    AUTH_GITHUB_LOGIN = EndpointSchemaConfig(
        primary_output_schema=LoginResponseSchema()
    )
    AUTH_GITHUB_LINK = EndpointSchemaConfig(
        input_schema=LinkToGithubRequestSchema(),
        input_dto_class=LinkToGithubRequestDTO,
        primary_output_schema=MessageSchema(),
    )
    # endregion
    REFRESH_SESSION = EndpointSchemaConfig(
        input_schema=RefreshSessionRequestSchema(),
        primary_output_schema=LoginResponseSchema(),
        input_dto_class=RefreshSessionRequestDTO,
    )
