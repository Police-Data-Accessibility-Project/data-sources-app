from enum import Enum
from http import HTTPStatus
from typing import Optional, Type

from marshmallow import Schema, RAISE

from middleware.primary_resource_logic.github_oauth_logic import (
    LinkToGithubRequestDTO,
)
from middleware.primary_resource_logic.permissions_logic import (
    PermissionsPutRequestSchema,
    PermissionsRequestDTO,
    PermissionsGetRequestSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.admin_dtos import (
    AdminUserPutDTO,
    AdminUserPostDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.archives_dtos import (
    ArchivesGetRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.bulk_dtos import (
    BulkRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.contact_dtos import (
    ContactFormPostDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.locations_dtos import (
    LocationPutDTO,
    LocationsGetRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.match_dtos import (
    AgencyMatchRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.reset_token_dtos import (
    ResetPasswordDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.source_collector_dtos import (
    SourceCollectorPostRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.admin_schemas import (
    AdminUsersGetByIDResponseSchema,
    AdminUsersPutSchema,
    AdminUsersPostSchema,
    AdminUsersGetManyResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_base_schemas import (
    GetManyAgenciesRequestsSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.archives_schemas import (
    ArchivesGetResponseSchema,
    ArchivesPutRequestSchema,
    ArchivesGetRequestSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.bulk_schemas import (
    BatchRequestSchema,
    BatchPostResponseSchema,
    AgenciesPostBatchRequestSchema,
    DataSourcesPostBatchRequestSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.contact_schemas import (
    ContactFormPostSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_base_schemas import (
    DataSourceRejectSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.locations_schemas import (
    GetLocationInfoByIDResponseSchema,
    LocationPutSchema,
    LocationsMapResponseSchema,
    LocationsGetManySchema,
    LocationsGetManyRequestSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.match_schemas import (
    AgencyMatchSchema,
    MatchAgencyResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.metrics_schemas import (
    MetricsGetResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.record_type_and_category_schemas import (
    RecordTypeAndCategoryResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.reset_token_schemas import (
    ResetPasswordSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.request_reset_password_dtos import (
    RequestResetPasswordRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.user_profile_dtos import (
    UserPutDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.api_key_schemas import (
    APIKeyResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.refresh_session_schemas import (
    RefreshSessionRequestSchema,
    RefreshSessionRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.request_reset_password_schemas import (
    RequestResetPasswordRequestSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.data_requests_dtos import (
    DataRequestsPutOuterDTO,
    RelatedSourceByIDDTO,
    RelatedLocationsByIDDTO,
    DataRequestsPostDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.source_collector_schemas import (
    SourceCollectorPostRequestSchema,
    SourceCollectorPostResponseSchema,
)

from middleware.schema_and_dto_logic.primary_resource_schemas.typeahead_suggestion_schemas import (
    TypeaheadAgenciesOuterResponseSchema,
    TypeaheadLocationsOuterResponseSchema,
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
    GithubOAuthRequestSchema,
    GithubOAuthRequestDTO,
    LoginWithGithubRequestDTO,
    GithubRequestSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.data_requests_dtos import (
    GetManyDataRequestsRequestsDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.notifications_schemas import (
    NotificationsResponseSchema,
)

from middleware.schema_and_dto_logic.primary_resource_schemas.search_schemas import (
    SearchRequestSchema,
    GetUserFollowedSearchesSchema,
    SearchRequestsDTO,
    SearchResponseSchema,
    FederalSearchRequestSchema,
    FederalSearchResponseSchema,
    FederalSearchRequestDTO,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
    GetManyBaseDTO,
    GetByIDBaseSchema,
    GetByIDBaseDTO,
    EntryDataRequestSchema,
    TypeaheadDTO,
    TypeaheadQuerySchema,
    EmailOnlyDTO,
    EmailOnlySchema,
    EntryCreateUpdateRequestDTO,
)
from middleware.schema_and_dto_logic.custom_types import DTOTypes
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_advanced_schemas import (
    AgenciesGetByIDResponseSchema,
    AgenciesPutSchema,
    AgenciesPostSchema,
    AgenciesGetManyResponseSchema,
    RelatedAgencyByIDSchema,
    AgenciesRelatedLocationSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.agencies_dtos import (
    AgenciesPostDTO,
    RelatedAgencyByIDDTO,
    AgenciesGetManyDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_advanced_schemas import (
    GetManyDataRequestsResponseSchema,
    DataRequestsPostSchema,
    GetByIDDataRequestsResponseSchema,
    GetManyDataRequestsRequestsSchema,
    DataRequestsRelatedLocationAddRemoveSchema,
    GetManyDataRequestsRelatedLocationsSchema,
    DataRequestsPutSchema,
    RelatedSourceByIDSchema,
)

from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_advanced_schemas import (
    DataSourcesGetManySchema,
    DataSourcesGetByIDSchema,
    DataSourcesPostSchema,
    DataSourcesPutSchema,
    DataSourcesGetManyRequestSchema,
    DataSourcesMapResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.data_sources_dtos import (
    DataSourcesPostDTO,
    DataSourcesRejectDTO,
)
from middleware.schema_and_dto_logic.common_response_schemas import (
    IDAndMessageSchema,
    MessageSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.github_issue_app_schemas import (
    GithubDataRequestsIssuesPostRequestSchema,
    GithubDataRequestsIssuesPostResponseSchema,
    GithubDataRequestsIssuesPostDTO,
    GithubSynchronizeResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.user_profile_schemas import (
    GetUserRecentSearchesOuterSchema,
    UserProfileResponseSchema,
    UserPutSchema,
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
        if "file" in self.input_schema.fields:
            load_file = True
        else:
            load_file = False
        return SchemaPopulateParameters(
            schema=self.input_schema,
            dto_class=self.input_dto_class,
            load_file=load_file,
        )


def get_post_resource_endpoint_schema_config(
    input_schema: Schema,
    input_dto_class: Type[DTOTypes],
) -> EndpointSchemaConfig:
    return EndpointSchemaConfig(
        input_schema=input_schema,
        primary_output_schema=IDAndMessageSchema(),
        input_dto_class=input_dto_class,
    )


def get_put_resource_endpoint_schema_config(
    input_schema: Schema,
    input_dto_class: Optional[Type[DTOTypes]] = None,
) -> EndpointSchemaConfig:
    return schema_config_with_message_output(
        input_schema=input_schema,
        input_dto_class=input_dto_class,
    )


def get_get_by_id_endpoint_schema_config(
    primary_output_schema: Schema,
) -> EndpointSchemaConfig:
    return EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        input_dto_class=GetByIDBaseDTO,
        primary_output_schema=primary_output_schema,
    )


def get_typeahead_schema_config(
    primary_output_schema: Schema,
) -> EndpointSchemaConfig:
    return EndpointSchemaConfig(
        input_schema=TypeaheadQuerySchema(),
        input_dto_class=TypeaheadDTO,
        primary_output_schema=primary_output_schema,
    )


def get_user_request_endpoint_schema_config(
    primary_output_schema: Schema,
) -> EndpointSchemaConfig:
    return EndpointSchemaConfig(
        input_schema=UserRequestSchema(),
        input_dto_class=UserRequestDTO,
        primary_output_schema=primary_output_schema,
    )


def schema_config_with_message_output(
    input_schema: Optional[Schema] = None,
    input_dto_class: Optional[Type[DTOTypes]] = None,
):
    return EndpointSchemaConfig(
        input_schema=input_schema,
        primary_output_schema=MessageSchema(),
        input_dto_class=input_dto_class,
    )


DELETE_BY_ID = schema_config_with_message_output(
    input_schema=GetByIDBaseSchema(),
)
DATA_SOURCES_RELATED_AGENCY_BY_ID = EndpointSchemaConfig(
    input_schema=RelatedAgencyByIDSchema(), input_dto_class=RelatedAgencyByIDDTO
)
SEARCH_FOLLOW_UPDATE = EndpointSchemaConfig(
    input_schema=SearchRequestSchema(
        exclude=["record_categories", "output_format"],
    ),
    input_dto_class=SearchRequestsDTO,
)


class SchemaConfigs(Enum):
    # region Data Requests
    DATA_REQUESTS_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyDataRequestsRequestsSchema(),
        primary_output_schema=GetManyDataRequestsResponseSchema(),
        input_dto_class=GetManyDataRequestsRequestsDTO,
    )
    DATA_REQUESTS_BY_ID_GET = get_get_by_id_endpoint_schema_config(
        primary_output_schema=GetByIDDataRequestsResponseSchema(),
    )
    DATA_REQUESTS_BY_ID_PUT = get_put_resource_endpoint_schema_config(
        input_schema=DataRequestsPutSchema(),
        input_dto_class=DataRequestsPutOuterDTO,
    )
    DATA_REQUESTS_BY_ID_WITHDRAW = schema_config_with_message_output()
    DATA_REQUESTS_BY_ID_DELETE = DELETE_BY_ID
    DATA_REQUESTS_POST = get_post_resource_endpoint_schema_config(
        input_schema=DataRequestsPostSchema(),
        input_dto_class=DataRequestsPostDTO,
    )
    DATA_REQUESTS_RELATED_SOURCES_GET = get_get_by_id_endpoint_schema_config(
        primary_output_schema=DataSourcesGetManySchema(
            exclude=["data.agencies"], partial=True
        ),
    )
    DATA_REQUESTS_RELATED_SOURCES_POST = EndpointSchemaConfig(
        input_schema=RelatedSourceByIDSchema(), input_dto_class=RelatedSourceByIDDTO
    )
    DATA_REQUESTS_RELATED_SOURCES_DELETE = EndpointSchemaConfig(
        input_schema=RelatedSourceByIDSchema(), input_dto_class=RelatedSourceByIDDTO
    )
    DATA_REQUESTS_RELATED_LOCATIONS_GET = get_get_by_id_endpoint_schema_config(
        primary_output_schema=GetManyDataRequestsRelatedLocationsSchema(),
    )
    DATA_REQUESTS_RELATED_LOCATIONS_POST = schema_config_with_message_output(
        input_schema=DataRequestsRelatedLocationAddRemoveSchema(),
        input_dto_class=RelatedLocationsByIDDTO,
    )
    DATA_REQUESTS_RELATED_LOCATIONS_DELETE = schema_config_with_message_output(
        input_schema=DataRequestsRelatedLocationAddRemoveSchema(),
        input_dto_class=RelatedLocationsByIDDTO,
    )

    # endregion
    # region Agencies
    AGENCIES_BY_ID_GET = get_get_by_id_endpoint_schema_config(
        primary_output_schema=AgenciesGetByIDResponseSchema(),
    )
    AGENCIES_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyAgenciesRequestsSchema(),
        primary_output_schema=AgenciesGetManyResponseSchema(),
        input_dto_class=AgenciesGetManyDTO,
    )
    AGENCIES_POST = get_post_resource_endpoint_schema_config(
        input_schema=AgenciesPostSchema(),
        input_dto_class=AgenciesPostDTO,
    )
    AGENCIES_BY_ID_PUT = get_put_resource_endpoint_schema_config(
        input_schema=AgenciesPutSchema(),
    )
    AGENCIES_BY_ID_DELETE = DELETE_BY_ID
    AGENCIES_BY_ID_RELATED_LOCATIONS_DELETE = EndpointSchemaConfig(
        input_schema=AgenciesRelatedLocationSchema(),
        primary_output_schema=MessageSchema(),
    )
    AGENCIES_BY_ID_RELATED_LOCATIONS_POST = EndpointSchemaConfig(
        input_schema=AgenciesRelatedLocationSchema(),
        primary_output_schema=MessageSchema(),
    )

    # endregion
    # region Data Sources
    DATA_SOURCES_GET_MANY = EndpointSchemaConfig(
        input_schema=DataSourcesGetManyRequestSchema(),
        primary_output_schema=DataSourcesGetManySchema(),
        input_dto_class=GetManyBaseDTO,
    )
    DATA_SOURCES_GET_BY_ID = get_get_by_id_endpoint_schema_config(
        primary_output_schema=DataSourcesGetByIDSchema(),
    )
    DATA_SOURCES_BY_ID_DELETE = DELETE_BY_ID
    DATA_SOURCES_POST = get_post_resource_endpoint_schema_config(
        input_schema=DataSourcesPostSchema(),
        input_dto_class=DataSourcesPostDTO,
    )
    DATA_SOURCES_MAP = EndpointSchemaConfig(
        primary_output_schema=DataSourcesMapResponseSchema(),
    )
    LOCATIONS_MAP = EndpointSchemaConfig(
        primary_output_schema=LocationsMapResponseSchema(),
    )
    LOCATIONS_GET_MANY = EndpointSchemaConfig(
        input_schema=LocationsGetManyRequestSchema(),
        input_dto_class=LocationsGetRequestDTO,
        primary_output_schema=LocationsGetManySchema(),
    )
    DATA_SOURCES_PUT = get_put_resource_endpoint_schema_config(
        input_schema=DataSourcesPutSchema(), input_dto_class=EntryDataRequestSchema
    )
    DATA_SOURCES_RELATED_AGENCIES_GET = get_get_by_id_endpoint_schema_config(
        primary_output_schema=AgenciesGetManyResponseSchema(
            exclude=["data.data_sources"]
        ),
    )
    DATA_SOURCES_RELATED_AGENCIES_POST = DATA_SOURCES_RELATED_AGENCY_BY_ID
    DATA_SOURCES_RELATED_AGENCIES_DELETE = DATA_SOURCES_RELATED_AGENCY_BY_ID
    DATA_SOURCES_BY_ID_REJECT = EndpointSchemaConfig(
        input_schema=DataSourceRejectSchema(),
        input_dto_class=DataSourcesRejectDTO,
        primary_output_schema=MessageSchema(),
    )
    # endregion

    # region Github
    GITHUB_DATA_REQUESTS_ISSUES_POST = EndpointSchemaConfig(
        input_schema=GithubDataRequestsIssuesPostRequestSchema(),
        primary_output_schema=GithubDataRequestsIssuesPostResponseSchema(),
        input_dto_class=GithubDataRequestsIssuesPostDTO,
    )
    GITHUB_DATA_REQUESTS_SYNCHRONIZE_POST = EndpointSchemaConfig(
        primary_output_schema=GithubSynchronizeResponseSchema(),
    )
    # endregion
    # region Search
    SEARCH_LOCATION_AND_RECORD_TYPE_GET = EndpointSchemaConfig(
        input_schema=SearchRequestSchema(),
        primary_output_schema=SearchResponseSchema(),
        input_dto_class=SearchRequestsDTO,
    )
    SEARCH_FEDERAL_GET = EndpointSchemaConfig(
        input_schema=FederalSearchRequestSchema(),
        primary_output_schema=FederalSearchResponseSchema(),
        input_dto_class=FederalSearchRequestDTO,
    )
    SEARCH_FOLLOW_GET = EndpointSchemaConfig(
        primary_output_schema=GetUserFollowedSearchesSchema(),
    )
    SEARCH_FOLLOW_POST = SEARCH_FOLLOW_UPDATE
    SEARCH_FOLLOW_DELETE = SEARCH_FOLLOW_UPDATE

    # endregion
    # region Typeahead
    TYPEAHEAD_LOCATIONS = get_typeahead_schema_config(
        primary_output_schema=TypeaheadLocationsOuterResponseSchema(),
    )
    TYPEAHEAD_AGENCIES = get_typeahead_schema_config(
        primary_output_schema=TypeaheadAgenciesOuterResponseSchema(),
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
    USER_PUT = get_put_resource_endpoint_schema_config(
        input_schema=UserPutSchema(),
        input_dto_class=UserPutDTO,
    )
    USER_PROFILE_RECENT_SEARCHES = EndpointSchemaConfig(
        primary_output_schema=GetUserRecentSearchesOuterSchema(exclude=["message"]),
    )
    USER_PROFILE_GET = EndpointSchemaConfig(
        primary_output_schema=UserProfileResponseSchema(),
    )
    USER_PROFILE_DATA_REQUESTS_GET = EndpointSchemaConfig(
        input_schema=GetManyRequestsBaseSchema(),
        input_dto_class=GetManyBaseDTO,
        primary_output_schema=GetManyDataRequestsResponseSchema(
            exclude=["data.internal_notes"]
        ),
    )

    # endregion
    # region Auth
    LOGIN_POST = get_user_request_endpoint_schema_config(
        primary_output_schema=LoginResponseSchema(),
    )
    AUTH_GITHUB_LOGIN = EndpointSchemaConfig(
        input_schema=GithubRequestSchema(),
        input_dto_class=LoginWithGithubRequestDTO,
        primary_output_schema=LoginResponseSchema(),
    )
    AUTH_GITHUB_LINK = schema_config_with_message_output(
        input_schema=LinkToGithubRequestSchema(),
        input_dto_class=LinkToGithubRequestDTO,
    )
    AUTH_GITHUB_OAUTH = EndpointSchemaConfig(
        input_schema=GithubOAuthRequestSchema(),
        input_dto_class=GithubOAuthRequestDTO,
    )
    AUTH_SIGNUP = get_user_request_endpoint_schema_config(
        primary_output_schema=MessageSchema(),
    )
    AUTH_VALIDATE_EMAIL = EndpointSchemaConfig(
        primary_output_schema=LoginResponseSchema(),
    )
    AUTH_RESEND_VALIDATION_EMAIL = schema_config_with_message_output(
        input_schema=EmailOnlySchema(),
        input_dto_class=EmailOnlyDTO,
    )

    # endregion
    REFRESH_SESSION = EndpointSchemaConfig(
        primary_output_schema=LoginResponseSchema(),
    )
    # region Reset Password
    REQUEST_RESET_PASSWORD = schema_config_with_message_output(
        input_schema=RequestResetPasswordRequestSchema(),
        input_dto_class=RequestResetPasswordRequestDTO,
    )
    RESET_PASSWORD = schema_config_with_message_output(
        input_schema=ResetPasswordSchema(),
        input_dto_class=ResetPasswordDTO,
    )
    RESET_TOKEN_VALIDATION = schema_config_with_message_output()
    API_KEY_POST = EndpointSchemaConfig(
        primary_output_schema=APIKeyResponseSchema(),
    )
    # endregion

    # region Archives
    ARCHIVES_GET = EndpointSchemaConfig(
        input_schema=ArchivesGetRequestSchema(),
        input_dto_class=ArchivesGetRequestDTO,
        primary_output_schema=ArchivesGetResponseSchema(many=True),
    )
    ARCHIVES_PUT = EndpointSchemaConfig(
        input_schema=ArchivesPutRequestSchema(),
    )
    # endregion

    # region Permission
    PERMISSIONS_GET = EndpointSchemaConfig(input_schema=PermissionsGetRequestSchema())
    PERMISSIONS_PUT = EndpointSchemaConfig(
        input_schema=PermissionsPutRequestSchema(),
        input_dto_class=PermissionsRequestDTO,
    )
    # endregion

    # region Batch
    BULK_DATA_SOURCES_POST = EndpointSchemaConfig(
        input_schema=DataSourcesPostBatchRequestSchema(),
        input_dto_class=DataSourcesPostDTO,
        primary_output_schema=BatchPostResponseSchema(),
    )
    BULK_AGENCIES_POST = EndpointSchemaConfig(
        input_schema=AgenciesPostBatchRequestSchema(),
        input_dto_class=AgenciesPostDTO,
        primary_output_schema=BatchPostResponseSchema(),
    )
    # endregion
    # region Match
    MATCH_AGENCY = EndpointSchemaConfig(
        input_schema=AgencyMatchSchema(),
        input_dto_class=AgencyMatchRequestDTO,
        primary_output_schema=MatchAgencyResponseSchema(),
    )
    # endregion

    # region Location
    LOCATIONS_BY_ID_GET = get_get_by_id_endpoint_schema_config(
        primary_output_schema=GetLocationInfoByIDResponseSchema(),
    )
    LOCATIONS_BY_ID_PUT = EndpointSchemaConfig(
        input_schema=LocationPutSchema(),
        input_dto_class=LocationPutDTO,
        primary_output_schema=MessageSchema(),
    )
    LOCATIONS_RELATED_DATA_REQUESTS_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        input_dto_class=GetByIDBaseDTO,
        primary_output_schema=GetManyDataRequestsResponseSchema(),
    )
    # endregion

    # region Metrics
    METRICS_GET = EndpointSchemaConfig(
        primary_output_schema=MetricsGetResponseSchema(),
    )

    # endregion

    # region Admin
    ADMIN_USERS_GET_MANY = EndpointSchemaConfig(
        input_schema=GetManyRequestsBaseSchema(),
        input_dto_class=GetManyBaseDTO,
        primary_output_schema=AdminUsersGetManyResponseSchema(),
    )

    ADMIN_USERS_BY_ID_GET = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        input_dto_class=GetByIDBaseDTO,
        primary_output_schema=AdminUsersGetByIDResponseSchema(),
    )

    ADMIN_USERS_BY_ID_PUT = EndpointSchemaConfig(
        input_schema=AdminUsersPutSchema(),
        input_dto_class=AdminUserPutDTO,
        primary_output_schema=MessageSchema(),
    )

    ADMIN_USERS_POST = get_post_resource_endpoint_schema_config(
        input_schema=AdminUsersPostSchema(),
        input_dto_class=AdminUserPostDTO,
    )

    ADMIN_USERS_BY_ID_DELETE = EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        input_dto_class=GetByIDBaseDTO,
        primary_output_schema=MessageSchema(),
    )

    # endregion

    # region Contact

    CONTACT_FORM_SUBMIT = EndpointSchemaConfig(
        input_schema=ContactFormPostSchema(),
        input_dto_class=ContactFormPostDTO,
        primary_output_schema=MessageSchema(),
    )

    # endregion

    # region Metadata
    RECORD_TYPE_AND_CATEGORY_GET = EndpointSchemaConfig(
        primary_output_schema=RecordTypeAndCategoryResponseSchema(),
    )
    # endregion

    PROPOSAL_AGENCIES_POST = EndpointSchemaConfig(
        input_schema=AgenciesPostSchema(
            exclude=[
                "agency_info.approval_status",
                "agency_info.last_approval_editor",
                "agency_info.submitter_contact",
                "agency_info.rejection_reason",
            ],
            unknown=RAISE,
        ),
        input_dto_class=AgenciesPostDTO,
    )

    SOURCE_COLLECTOR_DATA_SOURCES_POST = EndpointSchemaConfig(
        input_schema=SourceCollectorPostRequestSchema(),
        input_dto_class=SourceCollectorPostRequestDTO,
        primary_output_schema=SourceCollectorPostResponseSchema(),
    )
