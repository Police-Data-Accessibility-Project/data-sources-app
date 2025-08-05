from enum import Enum

from endpoints.instantiations.auth_.validate_email.endpoint_schema_config import (
    AuthValidateEmailEndpointSchema,
)
from endpoints.instantiations.source_collector.agencies.sync.schema_config import (
    SourceCollectorSyncAgenciesSchemaConfig,
)
from endpoints.instantiations.source_collector.data_sources.sync.schema_config import (
    SourceCollectorSyncDataSourceSchemaConfig,
)
from endpoints.instantiations.user.by_id.patch.endpoint_schema_config import (
    UserPatchEndpointSchemaConfig,
)
from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.schema_config.instantiations.admin.users.by_id.delete import (
    AdminUsersByIDDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.admin.users.by_id.put import (
    AdminUsersByIDPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.admin.users.get_many import (
    AdminUsersGetManyEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.admin.users.post import (
    AdminUsersPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.by_id.delete import (
    AgenciesByIDDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.by_id.get import (
    AgenciesByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.by_id.put import (
    AgenciesByIDPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.by_id.related_locations.delete import (
    AgenciesByIDRelatedLocationsDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.by_id.related_locations.post import (
    AgenciesByIDRelatedLocationsPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.get_many import (
    AgenciesGetManyEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.post import (
    AgenciesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.api_key import (
    ApiKeyPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.archives.get import (
    ArchivesGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.archives.put import (
    ArchivesPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.auth.github.link import (
    AuthGithubLinkEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.auth.github.login import (
    AuthGithubLoginEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.auth.github.oauth import (
    AuthGitHubOAuthEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.auth.login import LoginEndpointSchemaConfig
from endpoints.instantiations.auth_.resend_validation_email.endpoint_schema_config import (
    AuthResendValidationEmailEndpointSchemaConfig,
)
from endpoints.instantiations.auth_.signup.endpoint_schema_config import (
    AuthSignupEndpointSchemaConfig,
)

from endpoints.schema_config.instantiations.checker import (
    UniqueURLCheckerEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.contact import (
    ContactFormSubmitEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.by_id.delete import (
    DataRequestsByIDDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.by_id.get import (
    DataRequestsByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.by_id.put import (
    DataRequestsByIDPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.by_id.withdraw import (
    DataRequestsByIDWithdrawEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.get_many import (
    DataRequestsGetManyEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.post import (
    DataRequestsPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.related_locations.delete import (
    DataRequestsRelatedLocationsDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.related_locations.get import (
    DataRequestsRelatedLocationsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.related_locations.post import (
    DataRequestsRelatedLocationsPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.related_sources.get import (
    DataRequestsRelatedSourcesGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_requests.related_sources.post import (
    DataRequestsRelatedSourcesPost,
)
from endpoints.schema_config.instantiations.data_sources.by_id.agencies.delete import (
    DataSourcesRelatedAgenciesDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.by_id.agencies.get import (
    DataSourcesRelatedAgenciesGet,
)
from endpoints.schema_config.instantiations.data_sources.by_id.agencies.post import (
    DataSourcesRelatedAgenciesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.by_id.delete import (
    DataSourcesByIDDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.by_id.get import (
    DataSourcesByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.by_id.put import (
    DataSourcesByIDPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.by_id.reject import (
    DataSourcesByIDRejectEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.get_many import (
    DataSourcesGetManyEndpointSchemaConfig,
)
from endpoints.instantiations.map.data_sources.schema_config import (
    DataSourcesMapEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.post import (
    DataSourcesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.github.synchronize import (
    GitHubDataRequestsSynchronizePostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.by_id.get import (
    LocationsByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.by_id.put import (
    LocationsByIDPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.data_requests import (
    LocationsRelatedDataRequestsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.get_many import (
    LocationsGetManyEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.map import (
    LocationsMapEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.match import MatchAgencyEndpointSchemaConfig
from endpoints.schema_config.instantiations.metrics.followed_searches.aggregate import (
    MetricsFollowedSearchesAggregateGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.metrics.followed_searches.breakdown import (
    MetricsFollowedSearchesBreakdownGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.metrics.get import (
    MetricsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.notifications_.core import (
    NotificationsPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.notifications_.preview import (
    NotificationsPreviewEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.permissions.get import (
    PermissionsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.permissions.put import (
    PermissionsPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.proposal_agencies import (
    ProposalAgenciesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.record_type_and_category import (
    RecordTypeAndCategoryGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.reset_password.request import (
    RequestResetPasswordEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.reset_password.reset import (
    ResetPasswordEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.reset_password.validate import (
    ResetTokenValidationEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.federal import (
    SearchFederalGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.delete import (
    SearchFollowDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.get import (
    SearchFollowGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.national import (
    SearchFollowNationalEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.post import (
    SearchFollowPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.location_and_record_type import (
    SearchLocationAndRecordTypeGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.source_collector.data_sources import (
    SourceCollectorDataSourcesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.source_collector.duplicates import (
    SourceCollectorDuplicatesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.typeahead.agencies import (
    TypeaheadAgenciesEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.typeahead.locations import (
    TypeaheadLocationsEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.user.profile.data_requests import (
    UserProfileDataRequestsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.user.profile.get import (
    UserProfileGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.user.profile.recent_searches import (
    UserProfileRecentSearchesEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.user.put import UserPutEndpointSchemaConfig
from middleware.schema_and_dto.schemas.auth.login import LoginResponseSchema


class SchemaConfigs(Enum):
    # region Data Requests
    DATA_REQUESTS_GET_MANY = DataRequestsGetManyEndpointSchemaConfig
    DATA_REQUESTS_BY_ID_GET = DataRequestsByIDGetEndpointSchemaConfig
    DATA_REQUESTS_BY_ID_PUT = DataRequestsByIDPutEndpointSchemaConfig
    DATA_REQUESTS_BY_ID_WITHDRAW = DataRequestsByIDWithdrawEndpointSchemaConfig
    DATA_REQUESTS_BY_ID_DELETE = DataRequestsByIDDeleteEndpointSchemaConfig
    DATA_REQUESTS_POST = DataRequestsPostEndpointSchemaConfig
    DATA_REQUESTS_RELATED_SOURCES_GET = (
        DataRequestsRelatedSourcesGetEndpointSchemaConfig
    )
    DATA_REQUESTS_RELATED_SOURCES_POST = DataRequestsRelatedSourcesPost
    DATA_REQUESTS_RELATED_LOCATIONS_GET = (
        DataRequestsRelatedLocationsGetEndpointSchemaConfig
    )
    DATA_REQUESTS_RELATED_LOCATIONS_POST = (
        DataRequestsRelatedLocationsPostEndpointSchemaConfig
    )
    DATA_REQUESTS_RELATED_LOCATIONS_DELETE = (
        DataRequestsRelatedLocationsDeleteEndpointSchemaConfig
    )

    # endregion
    # region Agencies
    AGENCIES_BY_ID_GET = AgenciesByIDGetEndpointSchemaConfig
    AGENCIES_GET_MANY = AgenciesGetManyEndpointSchemaConfig
    AGENCIES_POST = AgenciesPostEndpointSchemaConfig
    AGENCIES_BY_ID_PUT = AgenciesByIDPutEndpointSchemaConfig
    AGENCIES_BY_ID_DELETE = AgenciesByIDDeleteEndpointSchemaConfig
    AGENCIES_BY_ID_RELATED_LOCATIONS_DELETE = (
        AgenciesByIDRelatedLocationsDeleteEndpointSchemaConfig
    )
    AGENCIES_BY_ID_RELATED_LOCATIONS_POST = (
        AgenciesByIDRelatedLocationsPostEndpointSchemaConfig
    )

    # endregion
    # region Data Sources
    DATA_SOURCES_GET_MANY = DataSourcesGetManyEndpointSchemaConfig
    DATA_SOURCES_GET_BY_ID = DataSourcesByIDGetEndpointSchemaConfig
    DATA_SOURCES_BY_ID_DELETE = DataSourcesByIDDeleteEndpointSchemaConfig
    DATA_SOURCES_POST = DataSourcesPostEndpointSchemaConfig
    DATA_SOURCES_MAP = DataSourcesMapEndpointSchemaConfig
    DATA_SOURCES_PUT = DataSourcesByIDPutEndpointSchemaConfig
    DATA_SOURCES_RELATED_AGENCIES_GET = DataSourcesRelatedAgenciesGet
    DATA_SOURCES_RELATED_AGENCIES_POST = (
        DataSourcesRelatedAgenciesPostEndpointSchemaConfig
    )
    DATA_SOURCES_RELATED_AGENCIES_DELETE = (
        DataSourcesRelatedAgenciesDeleteEndpointSchemaConfig
    )
    DATA_SOURCES_BY_ID_REJECT = DataSourcesByIDRejectEndpointSchemaConfig
    # endregion

    # region Github
    GITHUB_DATA_REQUESTS_SYNCHRONIZE_POST = (
        GitHubDataRequestsSynchronizePostEndpointSchemaConfig
    )
    # endregion
    # region Search
    SEARCH_LOCATION_AND_RECORD_TYPE_GET = (
        SearchLocationAndRecordTypeGetEndpointSchemaConfig
    )
    SEARCH_FEDERAL_GET = SearchFederalGetEndpointSchemaConfig
    SEARCH_FOLLOW_GET = SearchFollowGetEndpointSchemaConfig
    SEARCH_FOLLOW_POST = SearchFollowPostEndpointSchemaConfig
    SEARCH_FOLLOW_DELETE = SearchFollowDeleteEndpointSchemaConfig
    SEARCH_FOLLOW_NATIONAL = SearchFollowNationalEndpointSchemaConfig

    # endregion
    # region Typeahead
    TYPEAHEAD_LOCATIONS = TypeaheadLocationsEndpointSchemaConfig
    TYPEAHEAD_AGENCIES = TypeaheadAgenciesEndpointSchemaConfig
    # endregion
    # region Checker
    CHECKER_GET = UniqueURLCheckerEndpointSchemaConfig
    # endregion
    # region Notifications
    NOTIFICATIONS_POST = NotificationsPostEndpointSchemaConfig
    NOTIFICATIONS_PREVIEW = NotificationsPreviewEndpointSchemaConfig
    # region User Profile
    USER_PUT = UserPutEndpointSchemaConfig
    USER_PATCH = UserPatchEndpointSchemaConfig
    USER_PROFILE_RECENT_SEARCHES = UserProfileRecentSearchesEndpointSchemaConfig
    USER_PROFILE_GET = UserProfileGetEndpointSchemaConfig
    USER_PROFILE_DATA_REQUESTS_GET = UserProfileDataRequestsGetEndpointSchemaConfig

    # endregion
    # region Auth
    LOGIN_POST = LoginEndpointSchemaConfig
    AUTH_GITHUB_LOGIN = AuthGithubLoginEndpointSchemaConfig
    AUTH_GITHUB_LINK = AuthGithubLinkEndpointSchemaConfig
    AUTH_GITHUB_OAUTH = AuthGitHubOAuthEndpointSchemaConfig
    AUTH_SIGNUP = AuthSignupEndpointSchemaConfig
    AUTH_VALIDATE_EMAIL = AuthValidateEmailEndpointSchema
    AUTH_RESEND_VALIDATION_EMAIL = AuthResendValidationEmailEndpointSchemaConfig

    # endregion
    REFRESH_SESSION = EndpointSchemaConfig(
        primary_output_schema=LoginResponseSchema(),
    )
    # region Reset Password
    REQUEST_RESET_PASSWORD = RequestResetPasswordEndpointSchemaConfig
    RESET_PASSWORD = ResetPasswordEndpointSchemaConfig
    RESET_TOKEN_VALIDATION = ResetTokenValidationEndpointSchemaConfig
    API_KEY_POST = ApiKeyPostEndpointSchemaConfig
    # endregion

    # region Archives
    ARCHIVES_GET = ArchivesGetEndpointSchemaConfig
    ARCHIVES_PUT = ArchivesPutEndpointSchemaConfig
    # endregion

    # region Permission
    PERMISSIONS_GET = PermissionsGetEndpointSchemaConfig
    PERMISSIONS_PUT = PermissionsPutEndpointSchemaConfig
    # endregion
    # region Match
    MATCH_AGENCY = MatchAgencyEndpointSchemaConfig
    # endregion

    # region Location
    LOCATIONS_BY_ID_GET = LocationsByIDGetEndpointSchemaConfig
    LOCATIONS_BY_ID_PUT = LocationsByIDPutEndpointSchemaConfig
    LOCATIONS_RELATED_DATA_REQUESTS_GET = (
        LocationsRelatedDataRequestsGetEndpointSchemaConfig
    )
    LOCATIONS_MAP = LocationsMapEndpointSchemaConfig
    LOCATIONS_GET_MANY = LocationsGetManyEndpointSchemaConfig
    # endregion

    # region Metrics
    METRICS_GET = MetricsGetEndpointSchemaConfig
    METRICS_FOLLOWED_SEARCHES_BREAKDOWN_GET = (
        MetricsFollowedSearchesBreakdownGetEndpointSchemaConfig
    )
    METRICS_FOLLOWED_SEARCHES_AGGREGATE_GET = (
        MetricsFollowedSearchesAggregateGetEndpointSchemaConfig
    )

    # endregion

    # region Admin
    ADMIN_USERS_GET_MANY = AdminUsersGetManyEndpointSchemaConfig
    ADMIN_USERS_BY_ID_PUT = AdminUsersByIDPutEndpointSchemaConfig
    ADMIN_USERS_POST = AdminUsersPostEndpointSchemaConfig
    ADMIN_USERS_BY_ID_DELETE = AdminUsersByIDDeleteEndpointSchemaConfig
    # endregion

    # region Contact

    CONTACT_FORM_SUBMIT = ContactFormSubmitEndpointSchemaConfig
    # endregion

    # region Metadata
    RECORD_TYPE_AND_CATEGORY_GET = RecordTypeAndCategoryGetEndpointSchemaConfig
    # endregion

    PROPOSAL_AGENCIES_POST = ProposalAgenciesPostEndpointSchemaConfig

    SOURCE_COLLECTOR_DATA_SOURCES_POST = (
        SourceCollectorDataSourcesPostEndpointSchemaConfig
    )

    SOURCE_COLLECTOR_DUPLICATES_POST = SourceCollectorDuplicatesPostEndpointSchemaConfig
    SOURCE_COLLECTOR_SYNC_AGENCIES = SourceCollectorSyncAgenciesSchemaConfig
    SOURCE_COLLECTOR_SYNC_DATA_SOURCES = SourceCollectorSyncDataSourceSchemaConfig
