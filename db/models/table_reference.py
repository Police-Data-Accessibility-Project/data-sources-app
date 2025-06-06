from sqlalchemy import Column

from db.models.implementations.core import (
    Agency,
    AgencyExpanded,
    DataRequest,
    DataRequestExpanded,
    DataSource,
    DataSourceExpanded,
    DataSourceArchiveInfo,
    ResetToken,
    TestTable,
    User,
    USState,
    County,
    Locality,
    Location,
    LocationExpanded,
    ExternalAccount,
    DataRequestsGithubIssueInfo,
    DependentLocation,
    RecentSearch,
    RecordCategory,
    RecentSearchExpanded,
    RecordType,
    PendingUser,
    ChangeLog,
    NotificationLog,
    DistinctSourceURL,
)
from db.models.implementations.link import (
    LinkAgencyDataSource,
    LinkDataSourceDataRequest,
    LinkUserFollowedLocation,
    LinkLocationDataRequest,
    LinkRecentSearchRecordCategories,
    LinkRecentSearchRecordTypes,
    LinkLocationDataSourceView,
)
from middleware.enums import Relations

SQL_ALCHEMY_TABLE_REFERENCE = {
    "agencies": Agency,
    "agencies_expanded": AgencyExpanded,
    Relations.LINK_AGENCIES_DATA_SOURCES.value: LinkAgencyDataSource,
    Relations.LINK_LOCATIONS_DATA_REQUESTS.value: LinkLocationDataRequest,
    "data_requests": DataRequest,
    "data_requests_expanded": DataRequestExpanded,
    "data_sources": DataSource,
    "data_sources_expanded": DataSourceExpanded,
    "data_sources_archive_info": DataSourceArchiveInfo,
    "link_data_sources_data_requests": LinkDataSourceDataRequest,
    "reset_tokens": ResetToken,
    "test_table": TestTable,
    "users": User,
    "us_states": USState,
    "counties": County,
    "localities": Locality,
    "locations": Location,
    "locations_expanded": LocationExpanded,
    "link_user_followed_location": LinkUserFollowedLocation,
    "external_accounts": ExternalAccount,
    "data_requests_github_issue_info": DataRequestsGithubIssueInfo,
    Relations.DEPENDENT_LOCATIONS.value: DependentLocation,
    Relations.RECENT_SEARCHES.value: RecentSearch,
    Relations.LINK_RECENT_SEARCH_RECORD_CATEGORIES.value: LinkRecentSearchRecordCategories,
    Relations.LINK_RECENT_SEARCH_RECORD_TYPES.value: LinkRecentSearchRecordTypes,
    Relations.RECORD_CATEGORIES.value: RecordCategory,
    Relations.RECENT_SEARCHES_EXPANDED.value: RecentSearchExpanded,
    Relations.RECORD_TYPES.value: RecordType,
    Relations.PENDING_USERS.value: PendingUser,
    Relations.CHANGE_LOG.value: ChangeLog,
    Relations.NOTIFICATION_LOG.value: NotificationLog,
    Relations.LINK_LOCATIONS_DATA_SOURCES_VIEW.value: LinkLocationDataSourceView,
    Relations.DISTINCT_SOURCE_URLS.value: DistinctSourceURL,
}


def convert_to_column_reference(columns: list[str], relation: str) -> list[Column]:
    """Converts a list of column strings to SQLAlchemy column references.

    :param columns: List of column strings.
    :param relation: Relation string.
    :return:
    """
    try:
        relation_reference = SQL_ALCHEMY_TABLE_REFERENCE[relation]
    except KeyError:
        raise ValueError(
            f"SQL Model does not exist in SQL_ALCHEMY_TABLE_REFERENCE: {relation}"
        )

    def get_attribute(column: str) -> Column:
        try:
            return getattr(relation_reference, column)
        except AttributeError:
            raise AttributeError(
                f'Column "{column}" does not exist in SQLAlchemy Table Model for "{relation}"'
            )

    return [get_attribute(column) for column in columns]
