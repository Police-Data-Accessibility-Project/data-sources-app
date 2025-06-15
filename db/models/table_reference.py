from sqlalchemy import Column

from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.agency.expanded import AgencyExpanded
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_request.expanded import DataRequestExpanded
from db.models.implementations.core.data_request.github_issue_info import (
    DataRequestsGithubIssueInfo,
)
from db.models.implementations.core.data_source.archive import DataSourceArchiveInfo
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.data_source.expanded import DataSourceExpanded
from db.models.implementations.core.distinct_source_url import DistinctSourceURL
from db.models.implementations.core.external_account import ExternalAccount
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.county import County
from db.models.implementations.core.location.dependent import DependentLocation
from db.models.implementations.core.location.expanded import LocationExpanded
from db.models.implementations.core.location.locality import Locality
from db.models.implementations.core.location.us_state import USState
from db.models.implementations.core.log.change import ChangeLog
from db.models.implementations.core.log.notification import NotificationLog
from db.models.implementations.core.recent_search.core import RecentSearch
from db.models.implementations.core.record.category import RecordCategory
from db.models.implementations.core.record.type import RecordType
from db.models.implementations.core.reset_token import ResetToken
from db.models.implementations.core.test import TestTable
from db.models.implementations.core.user.core import User
from db.models.implementations.core.user.pending import PendingUser
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
