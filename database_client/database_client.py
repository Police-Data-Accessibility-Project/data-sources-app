from collections import namedtuple
from datetime import datetime
from enum import Enum
from functools import wraps, partialmethod
from http import HTTPStatus
from operator import and_, or_
from typing import Optional, Any, List, Callable, Union, Type
from psycopg import connection as PgConnection
import psycopg
import sqlalchemy.exc
from psycopg import sql, Cursor
from psycopg.rows import dict_row, tuple_row
from sqlalchemy import (
    select,
    delete,
    update,
    insert,
    Select,
    func,
    desc,
    asc,
    exists,
    union_all,
    case,
    text,
)
from sqlalchemy.orm import (
    aliased,
    load_only,
    selectinload,
    Session,
)
from werkzeug.exceptions import HTTPException, BadRequest

from database_client.DTOs import (
    UserInfoNonSensitive,
    UsersWithPermissions,
    DataRequestInfoForGithub,
)
from database_client.constants import (
    PAGE_SIZE,
    GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS,
)
from database_client.db_client_dataclasses import (
    OrderByParameters,
    WhereMapping,
)
from database_client.exceptions import LocationDoesNotExistError
from database_client.result_formatter import ResultFormatter
from database_client.subquery_logic import SubqueryParameters
from database_client.dynamic_query_constructor import DynamicQueryConstructor
from database_client.enums import (
    ExternalAccountTypeEnum,
    RequestStatus,
    EntityType,
    EventType,
    LocationType,
    ApprovalStatus,
    SortOrder,
)
from middleware.argument_checking_logic import check_for_mutually_exclusive_arguments
from middleware.custom_dataclasses import EventInfo, EventBatch
from middleware.exceptions import (
    UserNotFoundError,
    DuplicateUserError,
)
from database_client.models import (
    convert_to_column_reference,
    ExternalAccount,
    SQL_ALCHEMY_TABLE_REFERENCE,
    User,
    DataRequestExpanded,
    RecentSearch,
    LinkRecentSearchRecordCategories,
    RecordCategory,
    Agency,
    Location,
    LocationExpanded,
    TableCountLog,
    LinkRecentSearchRecordTypes,
    RecordType,
    LinkAgencyDataSource,
    LinkAgencyLocation,
    DataSourceExpanded,
    DataSource,
    DataRequest,
    LinkLocationDataRequest,
    LinkUserFollowedLocation,
    DataRequestsGithubIssueInfo,
    Base,
    DataSourceUserNotificationQueue,
    DataRequestUserNotificationQueue,
    DataRequestPendingEventNotification,
    DataSourcePendingEventNotification,
    NotificationLog,
    LinkLocationDataSourceView,
    DependentLocation,
)
from middleware.enums import (
    PermissionsEnum,
    Relations,
    AgencyType,
    RecordTypes,
    JurisdictionType,
    DataSourceCreationResponse,
)
from middleware.initialize_psycopg_connection import initialize_psycopg_connection
from middleware.initialize_sqlalchemy_session import initialize_sqlalchemy_session
from middleware.miscellaneous_logic.table_count_logic import (
    TableCountReference,
    TableCountReferenceManager,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.agencies_dtos import (
    AgenciesPostDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.locations_dtos import (
    LocationPutDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.match_dtos import (
    AgencyMatchResponseInnerDTO,
    AgencyMatchResponseLocationDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.metrics_dtos import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.source_collector_dtos import (
    SourceCollectorPostRequestInnerDTO,
    SourceCollectorPostResponseInnerDTO,
)
from middleware.util import get_env_variable
from utilities.enums import RecordCategories

DATA_SOURCES_MAP_COLUMN = [
    "data_source_id",
    "name",
    "agency_id",
    "agency_name",
    "state_iso",
    "municipality",
    "county_name",
    "record_type",
    "lat",
    "lng",
]


class DatabaseClient:

    def __init__(self):
        self.connection: PgConnection = initialize_psycopg_connection()
        self.session_maker = initialize_sqlalchemy_session()
        self.cursor: Optional[Cursor] = None

    def cursor_manager(row_factory=dict_row):
        """Decorator method for managing a cursor object.
        The cursor is closed after the method concludes its execution.

        :param row_factory: Row factory for the cursor, defaults to dict_row
        """

        def decorator(method):
            @wraps(method)
            def wrapper(self, *args, **kwargs):
                # Open a new cursor
                # If connection is closed, reopen
                if self.connection.closed != 0:
                    self.connection = initialize_psycopg_connection()
                self.cursor = self.connection.cursor(row_factory=row_factory)
                try:
                    # Execute the method
                    result = method(self, *args, **kwargs)
                    # Commit the transaction if no exception occurs
                    self.connection.commit()
                    return result
                except Exception as e:
                    # Rollback in case of an error
                    self.connection.rollback()
                    raise e
                finally:
                    # Close the cursor
                    self.cursor.close()
                    self.cursor = None

            return wrapper

        return decorator

    def session_manager(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            self.session = self.session_maker()
            try:
                result = method(self, *args, **kwargs)
                self.session.flush()
                self.session.commit()
                return result
            except Exception as e:
                self.session.rollback()
                raise e
            finally:
                self.session.close()
                self.session = None

        return wrapper

    @cursor_manager()
    def execute_raw_sql(
        self, query: str, vars: Optional[tuple] = None, execute_many: bool = False
    ) -> Optional[list[dict[Any, ...]]]:
        """Executes an SQL query passed to the function.

        :param query: The SQL query to execute.
        :param vars: A tuple of variables to replace placeholders in the SQL query, defaults to None
        :return: A list of dicts, or None if there are no results.
        """
        if execute_many:
            self.cursor.executemany(query, vars)
        else:
            self.cursor.execute(query, vars)
        try:
            results = self.cursor.fetchall()
        except psycopg.ProgrammingError:
            return None

        if len(results) == 0:
            return None
        return results

    @session_manager
    def execute_sqlalchemy(self, query: Callable):
        results = self.session.execute(query())
        return results

    def create_new_user(self, email: str, password_digest: str) -> Optional[int]:
        """
        Adds a new user to the database.
        :param email:
        :param password_digest:
        :return:
        """
        try:
            return self._create_entry_in_table(
                table_name="users",
                column_value_mappings={
                    "email": email,
                    "password_digest": password_digest,
                },
                column_to_return="id",
            )
        except sqlalchemy.exc.IntegrityError:
            raise DuplicateUserError

    def get_user_id(self, email: str) -> Optional[int]:
        """
        Gets the ID of a user in the database based on their email.
        :param email:
        :return:
        """
        results = self._select_from_relation(
            relation_name="users",
            columns=["id"],
            where_mappings=[WhereMapping(column="email", value=email)],
        )
        if len(results) == 0:
            return None
        return int(results[0]["id"])

    def update_user_password_digest(self, user_id: int, password_digest: str):
        """
        Updates the password digest for a user in the database.
        :param user_id:
        :param password_digest:
        :return:
        """
        self._update_entry_in_table(
            table_name="users",
            entry_id=user_id,
            column_edit_mappings={"password_digest": password_digest},
            id_column_name="id",
        )

    def get_password_digest(self, user_id: int) -> str:
        return self._select_single_entry_from_relation(
            relation_name=Relations.USERS.value,
            columns=["password_digest"],
            where_mappings={
                "id": user_id,
            },
        )["password_digest"]

    def password_digest_matches(self, user_id: int, password_digest: str) -> bool:
        db_password_digest = self._select_single_entry_from_relation(
            relation_name=Relations.USERS.value,
            columns=["password_digest"],
            where_mappings={
                "id": user_id,
            },
        )["password_digest"]
        return password_digest == db_password_digest

    ResetTokenInfo = namedtuple("ResetTokenInfo", ["id", "user_id", "create_date"])

    def get_reset_token_info(self, token: str) -> Optional[ResetTokenInfo]:
        """
        Checks if a reset token exists in the database and retrieves the associated user data.

        :param token: The reset token to check.
        :return: ResetTokenInfo if the token exists; otherwise, None.
        """
        results = self._select_from_relation(
            relation_name="reset_tokens",
            columns=["id", "user_id", "create_date"],
            where_mappings=[WhereMapping(column="token", value=token)],
        )
        if len(results) == 0:
            return None
        row = results[0]
        return self.ResetTokenInfo(
            id=row["id"], user_id=row["user_id"], create_date=row["create_date"]
        )

    def add_reset_token(self, user_id: int, token: str):
        """
        Inserts a new reset token into the database for a specified email.

        :param email: The email to associate with the reset token.
        :param token: The reset token to add.
        """
        self._create_entry_in_table(
            table_name="reset_tokens",
            column_value_mappings={"user_id": user_id, "token": token},
        )

    @cursor_manager()
    def delete_reset_token(self, user_id: int, token: str):
        """
        Deletes a reset token from the database for a specified email.

        :param email: The email associated with the reset token to delete.
        :param token: The reset token to delete.
        """
        query = sql.SQL(
            "delete from reset_tokens where user_id = {} and token = {}"
        ).format(sql.Literal(user_id), sql.Literal(token))
        self.cursor.execute(query)

    UserIdentifiers = namedtuple("UserIdentifiers", ["id", "email"])

    def get_user_by_api_key(self, api_key: str) -> Optional[UserIdentifiers]:
        """
        Get user id for a given api key
        :param api_key: The api key to check.
        :return: RoleInfo if the token exists; otherwise, None.
        """
        results = self._select_from_relation(
            relation_name="users",
            columns=["id", "email"],
            where_mappings=[WhereMapping(column="api_key", value=api_key)],
        )
        if len(results) == 0:
            return None
        return self.UserIdentifiers(id=results[0]["id"], email=results[0]["email"])

    def update_user_api_key(self, api_key: str, user_id: int):
        """
        Update the api key for a user
        :param api_key: The api key to check.
        :param user_id: The user id to update.
        """
        self._update_entry_in_table(
            table_name="users",
            entry_id=user_id,
            column_edit_mappings={"api_key": api_key},
        )

    MapInfo = namedtuple(
        "MapInfo",
        [
            "data_source_id",
            "location_id",
            "data_source_name",
            "agency_id",
            "agency_name",
            "state",
            "municipality",
            "county",
            "record_type",
            "lat",
            "lng",
        ],
    )

    @cursor_manager(row_factory=tuple_row)
    def get_data_sources_for_map(self) -> list[MapInfo]:
        """
        Returns a list of data sources with relevant info for the map from the database.

        :return: A list of MapInfo namedtuples, each containing details of a data source.
        """
        sql_query = """
            SELECT
                DATA_SOURCES.id AS DATA_SOURCE_ID,
                LE.ID as LOCATION_ID,
                DATA_SOURCES.NAME,
                AGENCIES.ID AS AGENCY_ID,
                AGENCIES.NAME AS AGENCY_NAME,
                LE.STATE_ISO,
                LE.LOCALITY_NAME AS MUNICIPALITY,
                LE.COUNTY_NAME,
                RT.NAME RECORD_TYPE,
                AGENCIES.LAT,
                AGENCIES.LNG
            FROM
                LINK_AGENCIES_DATA_SOURCES AS AGENCY_SOURCE_LINK
                INNER JOIN DATA_SOURCES ON AGENCY_SOURCE_LINK.DATA_SOURCE_ID = DATA_SOURCES.ID
                INNER JOIN AGENCIES ON AGENCY_SOURCE_LINK.AGENCY_ID = AGENCIES.ID
                INNER JOIN LINK_AGENCIES_LOCATIONS LAL ON AGENCIES.ID = LAL.AGENCY_ID
                LEFT JOIN LOCATIONS_EXPANDED LE ON LAL.LOCATION_ID = LE.ID
                INNER JOIN RECORD_TYPES RT ON RT.ID = DATA_SOURCES.RECORD_TYPE_ID
            WHERE
                DATA_SOURCES.APPROVAL_STATUS = 'approved'
                AND LAT is not null
				AND LNG is not null
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        return [self.MapInfo(*result) for result in results]

    @staticmethod
    def get_offset(page: int) -> Optional[int]:
        """
        Calculates the offset value for pagination based on the given page number.
        Args:
            page (int): The page number for which the offset is to be calculated. Starts at 0.
        Returns:
            int: The calculated offset value.
        Example:
            >>> get_offset(3)
            2000
        """
        if page is None:
            return None
        return (page - 1) * PAGE_SIZE

    ArchiveInfo = namedtuple(
        "ArchiveInfo",
        ["id", "url", "update_frequency", "last_cached", "broken_url_as_of"],
    )

    @cursor_manager()
    def get_data_sources_to_archive(
        self,
        update_frequency: Optional[str] = None,
        last_archived_before: Optional[datetime] = None,
        page: int = 1,
    ) -> list[ArchiveInfo]:
        """
        Pulls data sources to be archived by the automatic archives script.

        A data source is selected for archival if:
        The data source has been approved
        AND (
            the data source has not been archived previously
            OR the data source is updated regularly
        )
        AND the source url is not broken
        AND the source url is not null.

        :return: A list of ArchiveInfo namedtuples, each containing archive details of a data source.
        """
        sql_query = """
        SELECT
            data_sources.id,
            source_url,
            update_frequency,
            last_cached,
            broken_source_url_as_of
        FROM
            data_sources
        INNER JOIN
            data_sources_archive_info
        ON
            data_sources.id = data_sources_archive_info.data_source_id
        WHERE 
            approval_status = 'approved' AND (
                last_cached IS NULL 
                OR update_frequency IS NOT NULL
            )
            AND url_status <> 'broken' 
            AND source_url IS NOT NULL
        """

        if update_frequency is not None:
            sql_query += f" AND update_frequency = '{update_frequency.value}'"
        if last_archived_before is not None:
            sql_query += f" AND last_cached < '{last_archived_before}'"

        sql_query += f" LIMIT {PAGE_SIZE} OFFSET {self.get_offset(page)}"

        self.cursor.execute(sql_query)
        data_sources = self.cursor.fetchall()

        results = [
            self.ArchiveInfo(
                id=row["id"],
                url=row["source_url"],
                update_frequency=row["update_frequency"],
                last_cached=row["last_cached"],
                broken_url_as_of=row["broken_source_url_as_of"],
            )
            for row in data_sources
        ]

        return results

    def update_url_status_to_broken(self, id: str, broken_as_of: str) -> None:
        """
        Updates the data_sources table setting the url_status to 'broken' for a given id.

        :param id: The id of the data source.
        :param broken_as_of: The date when the source was identified as broken.
        """
        self.update_data_source(
            entry_id=id,
            column_edit_mappings={
                "url_status": "broken",
                "broken_source_url_as_of": broken_as_of,
            },
        )

    def update_last_cached(self, id: str, last_cached: str) -> None:
        """
        Updates the last_cached field in the data_sources_archive_info table for a given id.

        :param id: The id of the data source.
        :param last_cached: The last cached date to be updated.
        """
        self._update_entry_in_table(
            table_name=Relations.DATA_SOURCES_ARCHIVE_INFO.value,
            entry_id=id,
            column_edit_mappings={"last_cached": last_cached},
            id_column_name="data_source_id",
        )

    DataSourceMatches = namedtuple("DataSourceMatches", ["converted", "ids"])

    UserInfo = namedtuple("UserInfo", ["id", "password_digest", "api_key", "email"])

    def get_user_info(self, email: str) -> UserInfo:
        """
        Retrieves user data by email.

        :param email: User's email.
        :raise UserNotFoundError: If no user is found.
        :return: UserInfo namedtuple containing the user's information.
        """
        results = self._select_from_relation(
            relation_name="users",
            columns=["id", "password_digest", "api_key", "email"],
            where_mappings=[WhereMapping(column="email", value=email)],
        )
        if len(results) == 0:
            raise UserNotFoundError(email)
        result = results[0]

        return self.UserInfo(
            id=result["id"],
            password_digest=result["password_digest"],
            api_key=result["api_key"],
            email=result["email"],
        )

    @session_manager
    def get_user_info_by_external_account_id(
        self, external_account_id: str, external_account_type: ExternalAccountTypeEnum
    ) -> UserInfo:
        u = aliased(User)
        ea = aliased(ExternalAccount)

        query = (
            select(u.id, u.email, u.password_digest, u.api_key)
            .join(ea, u.id == ea.user_id)
            .where(
                ea.account_identifier == external_account_id,
                ea.account_type == external_account_type.value,
            )
        )
        results = self.session.execute(query).mappings().one_or_none()

        if results is None:
            raise UserNotFoundError(
                identifier=external_account_id, identifier_name="Github Account ID"
            )

        return self.UserInfo(
            id=results.id,
            password_digest=results.password_digest,
            api_key=results.api_key,
            email=results.email,
        )

    @cursor_manager()
    def get_typeahead_locations(self, search_term: str) -> dict:
        """
        Returns a list of data sources that match the search query.

        :param search_term: The search query.
        :return: List of data sources that match the search query.
        """
        query = DynamicQueryConstructor.generate_like_typeahead_locations_query(
            search_term
        )
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        if 0 < len(results) <= 10:
            return results

        fuzzy_match_query = (
            DynamicQueryConstructor.generate_fuzzy_match_typeahead_locations_query(
                search_term
            )
        )
        self.cursor.execute(fuzzy_match_query)
        return self.cursor.fetchall()

    @cursor_manager()
    def get_typeahead_agencies(self, search_term: str) -> dict:
        """
        Returns a list of data sources that match the search query.

        :param search_term: The search query.
        :return: List of agencies that match the search query.
        """
        query = DynamicQueryConstructor.generate_new_typeahead_agencies_query(
            search_term
        )
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @cursor_manager()
    def search_with_location_and_record_type(
        self,
        location_id: int,
        record_categories: Optional[list[RecordCategories]] = None,
        record_types: Optional[list[RecordTypes]] = None,
    ) -> List[dict]:
        """
        Searches for data sources in the database.

        :param state: The state to search for data sources in.
        :param record_categories: The types of data sources to search for. If None, all data sources will be searched for.
        :param county: The county to search for data sources in. If None, all data sources will be searched for.
        :param locality: The locality to search for data sources in. If None, all data sources will be searched for.
        :return: A list of dictionaries.
        """
        check_for_mutually_exclusive_arguments(record_categories, record_types)

        query = DynamicQueryConstructor.create_search_query(
            location_id=location_id,
            record_categories=record_categories,
            record_types=record_types,
        )
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @cursor_manager()
    def search_federal_records(
        self, record_categories: Optional[list[RecordCategories]] = None, page: int = 1
    ) -> List[dict]:
        query = DynamicQueryConstructor.create_federal_search_query(
            page=page,
            record_categories=record_categories,
        )
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def link_external_account(
        self,
        user_id: str,
        external_account_id: str,
        external_account_type: ExternalAccountTypeEnum,
    ):
        """
        Links an external account to a user.

        :param user_id: The ID of the user.
        :param external_account_id: The ID of the external account.
        :param external_account_type: The type of the external account.
        """
        self._create_entry_in_table(
            table_name="external_accounts",
            column_value_mappings={
                "user_id": user_id,
                "account_type": external_account_type.value,
                "account_identifier": external_account_id,
            },
        )

    @session_manager
    def get_table_count(self, table_name: str) -> int:
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        count = self.session.query(func.count(table.id)).scalar()
        return count

    @session_manager
    def log_table_counts(self, tcrs: list[TableCountReference]):
        # Add entry to TableCountLog
        for tcr in tcrs:
            new_entry = TableCountLog(table_name=tcr.table, count=tcr.count)
            self.session.add(new_entry)

    @session_manager
    def get_most_recent_logged_table_counts(self) -> TableCountReferenceManager:
        # Get the most recent table count for all distinct tables
        subquery = select(
            TableCountLog.table_name,
            TableCountLog.count,
            func.row_number()
            .over(
                partition_by=TableCountLog.table_name,
                order_by=desc(TableCountLog.created_at),
            )
            .label("row_num"),
        ).subquery()

        stmt = select(subquery.c.table_name, subquery.c.count).where(
            subquery.c.row_num == 1
        )

        results = self.session.execute(stmt).all()
        tcr = TableCountReferenceManager()
        for result in results:
            tcr.add_table_count(
                table_name=result[0],
                count=result[1],
            )
        return tcr

    @cursor_manager()
    def add_user_permission(self, user_id: str or int, permission: PermissionsEnum):
        """
        Adds a permission to a user.

        :param user_email: The email of the user.
        :param permission: The permission to add.
        """
        query = sql.SQL(
            """
            INSERT INTO user_permissions (user_id, permission_id) 
            VALUES (
                {id}, 
                (SELECT id FROM permissions WHERE permission_name = {permission})
            );
        """
        ).format(
            id=sql.Literal(user_id),
            permission=sql.Literal(permission.value),
        )
        self.cursor.execute(query)

    @cursor_manager()
    def remove_user_permission(self, user_id: str, permission: PermissionsEnum):
        query = sql.SQL(
            """
            DELETE FROM user_permissions
            WHERE user_id = {user_id}
            AND permission_id = (SELECT id FROM permissions WHERE permission_name = {permission});
        """
        ).format(
            user_id=sql.Literal(user_id),
            permission=sql.Literal(permission.value),
        )
        self.cursor.execute(query)

    @cursor_manager()
    def get_user_permissions(self, user_id: int) -> List[PermissionsEnum]:
        query = sql.SQL(
            """
            SELECT p.permission_name
            FROM 
            user_permissions up
            INNER JOIN permissions p on up.permission_id = p.id
            where up.user_id = {user_id}
        """
        ).format(
            user_id=sql.Literal(user_id),
        )
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [PermissionsEnum(row["permission_name"]) for row in results]

    @session_manager
    def _update_entry_in_table(
        self,
        table_name: str,
        entry_id: Any,
        column_edit_mappings: dict[str, Any],
        id_column_name: str = "id",
    ):
        """
        Updates a specific entry in a table in the database.

        :param table_name: The name of the table to update.
        :param entry_id: The ID of the entry to update.
        :param column_edit_mappings: A dictionary mapping column names to their new values.
        """
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        query_base = update(table)
        column = getattr(table, id_column_name)
        query_where = query_base.where(column == entry_id)
        query_values = query_where.values(**column_edit_mappings)
        self.session.execute(query_values)

    update_data_source = partialmethod(
        _update_entry_in_table, table_name="data_sources", id_column_name="id"
    )

    update_data_request = partialmethod(
        _update_entry_in_table,
        table_name="data_requests",
    )

    update_agency = partialmethod(
        _update_entry_in_table,
        table_name="agencies",
        id_column_name="id",
    )

    def update_dictionary_enum_values(self, d: dict):
        """
        Update a dictionary's values such that any which are enums are converted to the enum value
        Only works for flat, one-level dictionaries
        :param d:
        :return:
        """
        return {
            key: (value.value if isinstance(value, Enum) else value)
            for key, value in d.items()
        }

    @session_manager
    def _create_entry_in_table(
        self,
        table_name: str,
        column_value_mappings: dict[str, str],
        column_to_return: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Creates a new entry in a table in the database, using the provided column value mappings

        :param table_name: The name of the table to create an entry in.
        :param column_value_mappings: A dictionary mapping column names to their new values.
        """
        column_value_mappings = self.update_dictionary_enum_values(
            column_value_mappings
        )
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        statement = insert(table.__table__).values(**column_value_mappings)

        if column_to_return is not None:
            column = getattr(table, column_to_return)
            statement = statement.returning(column)
        result = self.session.execute(statement)

        if column_to_return is not None:
            return result.fetchone()[0]
        return None

    create_data_request = partialmethod(
        _create_entry_in_table, table_name="data_requests", column_to_return="id"
    )

    @session_manager
    def create_agency(
        self,
        dto: AgenciesPostDTO,
        user_id: Optional[int] = None,
    ):
        # Create Agency Entry
        agency_info = dto.agency_info
        agency = Agency(
            name=agency_info.name,
            agency_type=agency_info.agency_type.value,
            jurisdiction_type=agency_info.jurisdiction_type.value,
            multi_agency=agency_info.multi_agency,
            no_web_presence=agency_info.no_web_presence,
            approval_status=agency_info.approval_status.value,
            homepage_url=agency_info.homepage_url,
            lat=agency_info.lat,
            lng=agency_info.lng,
            defunct_year=agency_info.defunct_year,
            rejection_reason=agency_info.rejection_reason,
            last_approval_editor=agency_info.last_approval_editor,
            submitter_contact=agency_info.submitter_contact,
            creator_user_id=user_id,
        )
        self.session.add(agency)

        # Flush to get agency id
        self.session.flush()

        # Link to Locations
        if dto.location_ids is not None:
            for location_id in dto.location_ids:
                lal = LinkAgencyLocation(location_id=location_id, agency_id=agency.id)
                self.session.add(lal)

        return agency.id

    @session_manager
    def add_location_to_agency(self, location_id: int, agency_id: int):
        lal = LinkAgencyLocation(location_id=location_id, agency_id=agency_id)
        self.session.add(lal)

    @session_manager
    def remove_location_from_agency(self, location_id: int, agency_id: int):
        query = delete(LinkAgencyLocation).where(
            and_(
                LinkAgencyLocation.location_id == location_id,
                LinkAgencyLocation.agency_id == agency_id,
            )
        )
        self.session.execute(query)

    create_request_source_relation = partialmethod(
        _create_entry_in_table,
        table_name=Relations.LINK_DATA_SOURCES_DATA_REQUESTS.value,
        column_to_return="id",
    )

    create_data_source_agency_relation = partialmethod(
        _create_entry_in_table,
        table_name=Relations.LINK_AGENCIES_DATA_SOURCES.value,
        column_to_return="id",
    )

    create_request_location_relation = partialmethod(
        _create_entry_in_table,
        table_name=Relations.LINK_LOCATIONS_DATA_REQUESTS.value,
        column_to_return="id",
    )

    add_new_data_source = partialmethod(
        _create_entry_in_table,
        table_name="data_sources",
        column_to_return="id",
    )

    create_data_request_github_info = partialmethod(
        _create_entry_in_table,
        table_name=Relations.DATA_REQUESTS_GITHUB_ISSUE_INFO.value,
    )

    create_locality = partialmethod(
        _create_entry_in_table,
        table_name=Relations.LOCALITIES.value,
        column_to_return="id",
    )

    create_followed_search = partialmethod(
        _create_entry_in_table,
        table_name=Relations.LINK_USER_FOLLOWED_LOCATION.value,
    )

    def create_county(self, name: str, fips: str, state_id: int) -> int:
        """
        Create county and return county id
        """
        return self._create_entry_in_table(
            table_name=Relations.COUNTIES.value,
            column_value_mappings={"name": name, "fips": fips, "state_id": state_id},
            column_to_return="id",
        )

    @session_manager
    def _select_from_relation(
        self,
        relation_name: str,
        columns: list[str],
        where_mappings: Optional[Union[list[WhereMapping], dict]] = [True],
        limit: Optional[int] = PAGE_SIZE,
        page: Optional[int] = None,
        order_by: Optional[OrderByParameters] = None,
        subquery_parameters: Optional[list[SubqueryParameters]] = [],
        build_metadata: Optional[bool] = False,
        alias_mappings: Optional[dict[str, str]] = None,
        apply_uniqueness_constraints: Optional[bool] = True,
    ) -> list[dict]:
        """
        Selects a single relation from the database
        """
        limit = min(limit, 100)
        where_mappings = self._create_where_mappings_instance_if_dictionary(
            where_mappings
        )
        offset = self.get_offset(page)
        column_references = convert_to_column_reference(
            columns=columns, relation=relation_name
        )
        query = DynamicQueryConstructor.create_selection_query(
            relation_name,
            column_references,
            where_mappings,
            limit,
            offset,
            order_by,
            subquery_parameters,
            alias_mappings,
        )
        if apply_uniqueness_constraints:
            raw_results = self.session.execute(query()).mappings().unique().all()
        else:
            raw_results = self.session.execute(query()).mappings().all()
        results = self._process_results(
            build_metadata=build_metadata,
            raw_results=raw_results,
            relation_name=relation_name,
            subquery_parameters=subquery_parameters,
        )

        return results

    def _process_results(
        self,
        build_metadata: bool,
        raw_results: list,
        relation_name: str,
        subquery_parameters: Optional[list[SubqueryParameters]],
    ):
        table_key = self._build_table_key_if_results(raw_results)
        results = self._dictify_results(raw_results, subquery_parameters, table_key)
        results = self._optionally_build_metadata(
            build_metadata, relation_name, results, subquery_parameters
        )
        return results

    def _create_where_mappings_instance_if_dictionary(self, where_mappings):
        if isinstance(where_mappings, dict):
            where_mappings = WhereMapping.from_dict(where_mappings)
        return where_mappings

    def _optionally_build_metadata(
        self, build_metadata: bool, relation_name, results, subquery_parameters
    ):
        if build_metadata is True:
            results = ResultFormatter.format_with_metadata(
                results,
                relation_name,
                subquery_parameters,
            )
        return results

    def _dictify_results(
        self,
        raw_results: list,
        subquery_parameters: Optional[list[SubqueryParameters]],
        table_key: str,
    ):
        if subquery_parameters and table_key:
            # Calls models.Base.to_dict() method
            results = []
            for result in raw_results:
                val: dict = result[table_key].to_dict(subquery_parameters)
                self._alias_subqueries(subquery_parameters, val)
                results.append(val)
        else:
            results = [dict(result) for result in raw_results]
        return results

    def _alias_subqueries(self, subquery_parameters, val: dict):
        for sp in subquery_parameters:
            if sp.alias_mappings is None:
                continue
            for entry in val[sp.linking_column]:
                keys = list(entry.keys())
                for key in keys:
                    if key in sp.alias_mappings:
                        alias = sp.alias_mappings[key]
                        entry[alias] = entry[key]
                        del entry[key]

    def _build_table_key_if_results(self, raw_results: list) -> str:
        table_key = ""
        if len(raw_results) > 0:
            table_key = [key for key in raw_results[0].keys()][0]
        return table_key

    get_data_requests = partialmethod(
        _select_from_relation, relation_name=Relations.DATA_REQUESTS_EXPANDED.value
    )

    @session_manager
    def get_data_requests_ready_to_start_without_github_issue(
        self,
    ) -> list[DataRequestInfoForGithub]:
        query = (
            select(DataRequest)
            .where(
                and_(
                    DataRequest.request_status == RequestStatus.READY_TO_START.value,
                    DataRequestsGithubIssueInfo.id == None,
                )
            )
            .outerjoin(DataRequestsGithubIssueInfo)
            .options(selectinload(DataRequest.locations))
        )

        execute_results = self.session.execute(query).scalars()

        raw_results = execute_results.all()

        final_results = []
        for result in raw_results:
            display_names = []
            for location in result.locations:
                display_names.append(location.display_name)
            dto = DataRequestInfoForGithub(
                id=result.id,
                title=result.title,
                submission_notes=result.submission_notes,
                data_requirements=result.data_requirements,
                locations=display_names,
                record_types=result.record_types_required,
            )
            final_results.append(dto)

        return final_results

    @session_manager
    def get_agencies(
        self,
        order_by: Optional[OrderByParameters] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = PAGE_SIZE,
        requested_columns: Optional[list[str]] = None,
        approval_status: Optional[ApprovalStatus] = None,
    ):

        order_by_clause = DynamicQueryConstructor.get_sql_alchemy_order_by_clause(
            order_by=order_by,
            relation=Relations.AGENCIES.value,
            default=asc(Agency.id),
        )

        load_options = DynamicQueryConstructor.agencies_get_load_options(
            requested_columns=requested_columns
        )

        # TODO: This format can be extracted to a function (see get_data_sources)
        query = select(Agency)

        if approval_status is not None:
            query = query.where(Agency.approval_status == approval_status.value)

        query = (
            query.options(*load_options)
            .order_by(order_by_clause)
            .limit(limit)
            .offset(self.get_offset(page))
        )

        results: list[Agency] = self.session.execute(query).scalars(Agency).all()
        final_results = []
        for result in results:
            agency_dictionary = ResultFormatter.agency_to_get_agencies_output(
                result, requested_columns=requested_columns
            )
            final_results.append(agency_dictionary)

        return final_results

    @session_manager
    def get_agency_by_id(
        self,
        agency_id: int,
    ):

        load_options = DynamicQueryConstructor.agencies_get_load_options()

        query = select(Agency).options(*load_options).where(Agency.id == agency_id)

        result: Agency = self.session.execute(query).scalars(Agency).first()
        agency_dictionary = ResultFormatter.agency_to_get_agencies_output(
            result,
        )

        return agency_dictionary

    @session_manager
    def get_data_sources(
        self,
        data_sources_columns: list[str],
        data_requests_columns: list[str],
        order_by: Optional[OrderByParameters] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = PAGE_SIZE,
        approval_status: Optional[ApprovalStatus] = None,
    ):

        order_by_clause = DynamicQueryConstructor.get_sql_alchemy_order_by_clause(
            order_by=order_by,
            relation=Relations.DATA_SOURCES.value,
            default=asc(DataSourceExpanded.id),
        )

        load_options = DynamicQueryConstructor.data_sources_get_load_options(
            data_requests_columns=data_requests_columns,
            data_sources_columns=data_sources_columns,
        )

        # TODO: This format can be extracted to a function (see get_agencies)
        query = select(DataSourceExpanded)

        if approval_status is not None:
            query = query.where(
                DataSourceExpanded.approval_status == approval_status.value
            )

        query = (
            query.options(*load_options).order_by(order_by_clause).limit(limit)
        ).offset(self.get_offset(page))

        results: list[DataSourceExpanded] = (
            self.session.execute(query).scalars(DataSource).all()
        )
        final_results = []
        for result in results:
            data_source_dictionary = (
                ResultFormatter.data_source_to_get_data_sources_output(
                    result,
                    data_sources_columns=data_sources_columns,
                    data_requests_columns=data_requests_columns,
                )
            )
            final_results.append(data_source_dictionary)

        return final_results

    @session_manager
    def get_data_source_related_agencies(
        self,
        data_source_id: int,
    ) -> Optional[list[dict]]:
        query = (
            select(DataSourceExpanded)
            .options(
                selectinload(DataSourceExpanded.agencies).selectinload(Agency.locations)
            )
            .where(DataSourceExpanded.id == data_source_id)
        )

        result: DataSourceExpanded = (
            self.session.execute(query).scalars(DataSourceExpanded).first()
        )
        if result is None:
            return None

        agency_dicts = []
        for agency in result.agencies:
            agency_dict = (
                ResultFormatter.agency_to_data_sources_get_related_agencies_output(
                    agency
                )
            )
            agency_dicts.append(agency_dict)

        return agency_dicts

    @session_manager
    def get_data_source_by_id(
        self,
        data_source_id: int,
        data_sources_columns: list[str],
        data_requests_columns: list[str],
    ):
        load_options = DynamicQueryConstructor.data_sources_get_load_options(
            data_sources_columns=data_sources_columns,
            data_requests_columns=data_requests_columns,
        )

        query = (
            select(DataSourceExpanded)
            .options(*load_options)
            .where(DataSourceExpanded.id == data_source_id)
        )

        result: DataSourceExpanded = (
            self.session.execute(query).scalars(DataSourceExpanded).first()
        )
        if result is None:
            return None

        data_source_dictionary = ResultFormatter.data_source_to_get_data_sources_output(
            result,
            data_requests_columns=data_requests_columns,
            data_sources_columns=data_sources_columns,
        )

        return data_source_dictionary

    get_request_source_relations = partialmethod(
        _select_from_relation, relation_name=Relations.RELATED_SOURCES.value
    )

    def _select_single_entry_from_relation(
        self,
        relation_name: str,
        columns: list[str],
        where_mappings: Optional[Union[list[WhereMapping], dict]] = [True],
        subquery_parameters: Optional[list[SubqueryParameters]] = [],
        **kwargs,
    ) -> Any:
        results = self._select_from_relation(
            relation_name=relation_name,
            columns=columns,
            where_mappings=where_mappings,
            subquery_parameters=subquery_parameters,
            **kwargs,
        )
        if len(results) == 0:
            return None
        if len(results) > 1:
            raise RuntimeError(f"Expected 1 result but found {len(results)}")
        return results[0]

    def get_location_id(
        self, where_mappings: Union[list[WhereMapping], dict]
    ) -> Optional[int]:
        result = self._select_single_entry_from_relation(
            relation_name=Relations.LOCATIONS_EXPANDED.value,
            columns=["id"],
            where_mappings=where_mappings,
        )
        if result is None:
            return None
        return result["id"]

    def get_related_data_sources(self, data_request_id: int) -> List[dict]:
        """
        Get data sources related to the request id
        :param data_request_id:
        :return:
        """
        query = sql.SQL(
            """
            SELECT ds.id, ds.name
            FROM link_data_sources_data_requests link
            INNER JOIN data_sources ds on link.data_source_id = ds.id
            WHERE link.request_id = {request_id}
        """
        ).format(request_id=sql.Literal(data_request_id))
        return self.execute_composed_sql(query, return_results=True)

    def get_data_requests_for_creator(
        self, creator_user_id: str, columns: List[str]
    ) -> List[str]:
        return self._select_from_relation(
            relation_name="data_requests",
            columns=columns,
            where_mappings=[
                WhereMapping(column="creator_user_id", value=creator_user_id)
            ],
        )

    def user_is_creator_of_data_request(
        self, user_id: int, data_request_id: int
    ) -> bool:
        results = self._select_from_relation(
            relation_name="data_requests",
            columns=["id"],
            where_mappings=[
                WhereMapping(column="creator_user_id", value=int(user_id)),
                WhereMapping(column="id", value=int(data_request_id)),
            ],
        )
        return len(results) == 1

    # @cursor_manager()
    @session_manager
    def _delete_from_table(
        self,
        table_name: str,
        id_column_value: str | int,
        id_column_name: str = "id",
    ):
        """
        Deletes an entry from a table in the database
        """
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        column = getattr(table, id_column_name)
        query = delete(table).where(column == id_column_value)
        self.session.execute(query)

    delete_data_request = partialmethod(_delete_from_table, table_name="data_requests")

    delete_agency = partialmethod(_delete_from_table, table_name="agencies")

    delete_data_source = partialmethod(_delete_from_table, table_name="data_sources")

    delete_request_source_relation = partialmethod(
        _delete_from_table, table_name=Relations.RELATED_SOURCES.value
    )

    delete_request_location_relation = partialmethod(
        _delete_from_table, table_name=Relations.LINK_LOCATIONS_DATA_REQUESTS.value
    )

    delete_followed_search = partialmethod(
        _delete_from_table, table_name=Relations.LINK_USER_FOLLOWED_LOCATION.value
    )

    delete_data_source_agency_relation = partialmethod(
        _delete_from_table, table_name=Relations.LINK_AGENCIES_DATA_SOURCES.value
    )

    @cursor_manager()
    def execute_composed_sql(self, query: sql.Composed, return_results: bool = False):
        self.cursor.execute(query)
        if return_results:
            return self.cursor.fetchall()

    def get_agencies_without_homepage_urls(self) -> list[dict]:
        return self.execute_raw_sql(
            """
            SELECT
                SUBMITTED_NAME,
                JURISDICTION_TYPE,
                STATE_ISO,
                LOCALITY_NAME as MUNICIPALITY,
                COUNTY_NAME,
                ID,
                ZIP_CODE,
                NO_WEB_PRESENCE -- Relevant
            FROM
                PUBLIC.AGENCIES_EXPANDED 
                INNER JOIN NUM_DATA_SOURCES_PER_AGENCY num ON num.agency_uid = AGENCIES_EXPANDED.id 
            WHERE 
                approved = true
                AND homepage_url is null
                AND NOT EXISTS (
                    SELECT 1 FROM PUBLIC.AGENCY_URL_SEARCH_CACHE
                    WHERE PUBLIC.AGENCIES_EXPANDED.id = PUBLIC.AGENCY_URL_SEARCH_CACHE.agency_id
                )
            ORDER BY NUM.DATA_SOURCE_COUNT DESC
            LIMIT 100 -- Limiting to 100 in acknowledgment of the search engine quota
        """
        )

    @cursor_manager()
    def check_for_url_duplicates(self, url: str) -> list[dict]:
        query = DynamicQueryConstructor.get_distinct_source_urls_query(url)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_columns_for_relation(self, relation: Relations) -> list[dict]:
        """
        Get columns for a given relation
        :param relation:
        :return:
        """
        results = self.execute_raw_sql(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = %s
        """,
            (relation.value,),
        )

        return [row["column_name"] for row in results]

    def get_county_id(self, county_name: str, state_id: int) -> int:
        return self._select_single_entry_from_relation(
            relation_name=Relations.COUNTIES.value,
            columns=["id"],
            where_mappings=[
                WhereMapping(column="name", value=county_name),
                WhereMapping(column="state_id", value=state_id),
            ],
        )

    def create_or_get(
        self,
        table_name: str,
        column_value_mappings: dict[str, str],
        column_to_return: str = "id",
    ):
        """
        Create a value and return the id if it doesn't exist; if it does, return the id for it
        :param table_name:
        :param column_value_mappings:
        :param column_to_return:
        :return:
        """
        try:
            return self._create_entry_in_table(
                table_name=table_name,
                column_value_mappings=column_value_mappings,
                column_to_return=column_to_return,
            )
        except sqlalchemy.exc.IntegrityError:
            return self._select_from_relation(
                relation_name=table_name,
                columns=[column_to_return],
                where_mappings=WhereMapping.from_dict(column_value_mappings),
            )[0][column_to_return]

    def get_linked_rows(
        self,
        link_table: Relations,
        left_id: str,
        left_link_column: str,
        right_link_column: str,
        linked_relation: Relations,
        linked_relation_linking_column: str,
        columns_to_retrieve: list[str],
        alias_mappings: Optional[dict[str, str]] = None,
        build_metadata=False,
        subquery_parameters: Optional[list[SubqueryParameters]] = [],
    ):
        # Get ids via linked table
        link_results = self._select_from_relation(
            relation_name=link_table.value,
            columns=[right_link_column],
            where_mappings={left_link_column: left_id},
        )
        link_ids = [result[right_link_column] for result in link_results]
        linked_results = self._select_from_relation(
            relation_name=linked_relation.value,
            columns=columns_to_retrieve,
            alias_mappings=alias_mappings,
            where_mappings={linked_relation_linking_column: link_ids},
            build_metadata=build_metadata,
            subquery_parameters=subquery_parameters,
        )
        return linked_results

    def _build_column_references(
        self, LinkedRelation, alias_mappings, columns_to_retrieve
    ):
        column_references = []
        for column in columns_to_retrieve:
            column_reference = getattr(LinkedRelation, column)
            if alias_mappings is not None and column in alias_mappings:
                column_reference = column_reference.label(alias_mappings[column])
            column_references.append(column_reference)
        return column_references

    get_user_followed_searches = partialmethod(
        get_linked_rows,
        link_table=Relations.LINK_USER_FOLLOWED_LOCATION,
        left_link_column="user_id",
        right_link_column="location_id",
        linked_relation=Relations.LOCATIONS_EXPANDED,
        linked_relation_linking_column="id",
        columns_to_retrieve=["state_name", "county_name", "locality_name", "id"],
        build_metadata=True,
        alias_mappings={"id": "location_id"},
    )

    DataRequestIssueInfo = namedtuple(
        "DataRequestIssueInfo",
        [
            "data_request_id",
            "github_issue_url",
            "github_issue_number",
            "request_status",
            "record_types_required",
        ],
    )

    @session_manager
    def get_unarchived_data_requests_with_issues(self) -> list[DataRequestIssueInfo]:
        dre = aliased(DataRequestExpanded)

        select_statement = select(
            dre.id,
            dre.github_issue_url,
            dre.github_issue_number,
            dre.request_status,
            dre.record_types_required,
        )

        with_filter = select_statement.where(
            and_(
                dre.request_status != RequestStatus.ARCHIVED.value,
                dre.github_issue_url != None,
            )
        )

        results = self.session.execute(with_filter).mappings().all()

        return [
            self.DataRequestIssueInfo(
                data_request_id=result["id"],
                github_issue_url=result["github_issue_url"],
                github_issue_number=result["github_issue_number"],
                request_status=RequestStatus(result["request_status"]),
                record_types_required=result["record_types_required"],
            )
            for result in results
        ]

    @session_manager
    def optionally_update_user_notification_queue(self):
        """
        Clears and repopulates the user notification queue with new notifications
        :return:
        """
        # Get all data requests associated with the user's location that have a corresponding event
        # (and that event is not already in user_notification_queue for that user)
        data_request_query = (
            select(
                DataRequestPendingEventNotification.id.label("event_id"),
                User.id.label("user_id"),
            )
            .join(
                DataRequest,
                DataRequest.id == DataRequestPendingEventNotification.data_request_id,
            )
            .join(
                LinkLocationDataRequest,
                LinkLocationDataRequest.data_request_id == DataRequest.id,
            )
            .join(Location, Location.id == LinkLocationDataRequest.location_id)
            .join(
                LinkUserFollowedLocation,
                LinkUserFollowedLocation.location_id == Location.id,
            )
            .join(User, User.id == LinkUserFollowedLocation.user_id)
            .where(
                # Event ID should not be in user_notification_queue for that user
                DataRequestPendingEventNotification.id.notin_(
                    select(DataRequestUserNotificationQueue.event_id).where(
                        DataRequestUserNotificationQueue.user_id == User.id
                    )
                )
            )
        )

        raw_results = self.session.execute(data_request_query).mappings().all()
        for result in raw_results:
            queue = DataRequestUserNotificationQueue(
                user_id=result["user_id"],
                event_id=result["event_id"],
            )
            self.session.add(queue)
        self.session.flush()

        data_source_query = (
            select(
                DataSourcePendingEventNotification.id.label("event_id"),
                User.id.label("user_id"),
            )
            .join(
                DataSource,
                DataSource.id == DataSourcePendingEventNotification.data_source_id,
            )
            .join(
                LinkAgencyDataSource,
                LinkAgencyDataSource.data_source_id == DataSource.id,
            )
            .join(Agency, Agency.id == LinkAgencyDataSource.agency_id)
            .join(LinkAgencyLocation, LinkAgencyLocation.agency_id == Agency.id)
            .join(Location, Location.id == LinkAgencyLocation.location_id)
            .join(
                LinkUserFollowedLocation,
                LinkUserFollowedLocation.location_id == Location.id,
            )
            .join(User, User.id == LinkUserFollowedLocation.user_id)
            .where(
                # Event ID should not be in user_notification_queue for that user
                DataSourcePendingEventNotification.id.notin_(
                    select(DataSourceUserNotificationQueue.event_id).where(
                        DataSourceUserNotificationQueue.user_id == User.id
                    )
                )
            )
        )

        raw_results = self.session.execute(data_source_query).mappings().all()
        for result in raw_results:
            queue = DataSourceUserNotificationQueue(
                user_id=result["user_id"],
                event_id=result["event_id"],
            )
            self.session.add(queue)

    @session_manager
    def get_next_user_event_batch(self) -> Optional[EventBatch]:
        """
        Get next user

        """
        query = (
            select(User)
            .where(
                or_(
                    exists(
                        select(DataSourceUserNotificationQueue.id).where(
                            and_(
                                DataSourceUserNotificationQueue.user_id == User.id,
                                DataSourceUserNotificationQueue.sent_at.is_(None),
                            )
                        )
                    ),
                    exists(
                        select(DataRequestUserNotificationQueue.id).where(
                            and_(
                                DataRequestUserNotificationQueue.user_id == User.id,
                                DataRequestUserNotificationQueue.sent_at.is_(None),
                            )
                        )
                    ),
                )
            )
            .options(
                selectinload(User.data_request_events),
                selectinload(User.data_source_events),
            )
            .limit(1)
        )

        raw_results = self.session.execute(query).first()
        if raw_results is None:
            return None
        user = raw_results[0]
        event_infos = []
        for event in user.data_request_events:
            event_info = EventInfo(
                event_id=event.id,
                event_type=EventType(event.event_type),
                entity_id=event.data_request.id,
                entity_type=EntityType.DATA_REQUEST,
                entity_name=event.data_request.title,
            )
            event_infos.append(event_info)
        for event in user.data_source_events:
            event_info = EventInfo(
                event_id=event.id,
                event_type=EventType(event.event_type),
                entity_id=event.data_source.id,
                entity_type=EntityType.DATA_SOURCE,
                entity_name=event.data_source.name,
            )
            event_infos.append(event_info)
        return EventBatch(user_id=user.id, user_email=user.email, events=event_infos)

    @session_manager
    def mark_user_events_as_sent(self, user_id: int):

        with self.session.begin():
            for queue in (
                DataRequestUserNotificationQueue,
                DataSourceUserNotificationQueue,
            ):
                self.session.query(queue).filter(queue.user_id == user_id).update(
                    {queue.sent_at: datetime.now()}
                )

    @session_manager
    def create_search_record(
        self,
        user_id: int,
        location_id: int,
        record_categories: Optional[
            Union[list[RecordCategories], RecordCategories]
        ] = None,
        record_types: Optional[Union[list[RecordTypes], RecordTypes]] = None,
    ):
        if isinstance(record_categories, RecordCategories):
            record_categories = [record_categories]

        with self.session.begin():
            # Insert into recent_search table and get recent_search_id
            query = (
                insert(RecentSearch)
                .values({"user_id": user_id, "location_id": location_id})
                .returning(RecentSearch.id)
            )
            result = self.session.execute(query)
            recent_search_id = result.fetchone()[0]

            if record_categories is not None:
                self.insert_record_category_search_records(
                    recent_search_id, record_categories
                )
            if record_types is not None:
                self.insert_record_type_search_records(recent_search_id, record_types)

    def insert_record_type_search_records(self, recent_search_id, record_types):
        # For all record types, insert into link table
        for record_type in record_types:
            query = select(RecordType).filter(RecordType.name == record_type.value)
            rt_id = self.session.execute(query).fetchone()[0].id

            query = insert(LinkRecentSearchRecordTypes).values(
                {"recent_search_id": recent_search_id, "record_type_id": rt_id}
            )
            self.session.execute(query)

    def insert_record_category_search_records(
        self, recent_search_id, record_categories
    ):
        # For all record types, insert into link table
        for record_type in record_categories:
            query = select(RecordCategory).filter(
                RecordCategory.name == record_type.value
            )
            rc_id = self.session.execute(query).fetchone()[0].id

            query = insert(LinkRecentSearchRecordCategories).values(
                {"recent_search_id": recent_search_id, "record_category_id": rc_id}
            )
            self.session.execute(query)

    def get_user_recent_searches(self, user_id: int):
        return self._select_from_relation(
            relation_name=Relations.RECENT_SEARCHES_EXPANDED.value,
            columns=[
                "location_id",
                "state_name",
                "county_name",
                "locality_name",
                "location_type",
                "record_categories",
            ],
            where_mappings={"user_id": user_id},
            build_metadata=True,
        )

    def get_record_type_id_by_name(self, record_type_name: str):
        return self._select_single_entry_from_relation(
            relation_name=Relations.RECORD_TYPES.value,
            columns=["id"],
            where_mappings={"name": record_type_name},
        )["id"]

    def get_user_external_accounts(self, user_id: int):
        raw_results = self._select_from_relation(
            relation_name=Relations.EXTERNAL_ACCOUNTS.value,
            columns=["account_type", "account_identifier"],
            where_mappings={"user_id": user_id},
        )
        return {row["account_type"]: row["account_identifier"] for row in raw_results}

    def get_user_info_by_id(self, user_id: int) -> UserInfoNonSensitive:
        result = self._select_single_entry_from_relation(
            relation_name=Relations.USERS.value,
            columns=[
                "email",
                "created_at",
                "updated_at",
            ],
            where_mappings={"id": user_id},
        )
        return UserInfoNonSensitive(
            user_id=user_id,
            email=result["email"],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
        )

    def get_change_logs_for_table(self, table: Relations):
        return self._select_from_relation(
            relation_name=Relations.CHANGE_LOG.value,
            columns=[
                "id",
                "operation_type",
                "table_name",
                "affected_id",
                "old_data",
                "new_data",
                "created_at",
            ],
            where_mappings={"table_name": table.value},
            apply_uniqueness_constraints=False,
        )

    @session_manager
    def get_users(self, page: int) -> List[UsersWithPermissions]:
        raw_results = self.session.execute(
            select(User)
            .options(selectinload(User.permissions))
            .order_by(User.created_at.desc())
            .limit(100)
            .offset((page - 1) * 100)
        ).all()

        final_results = []

        for raw_result in raw_results:
            user = raw_result[0]
            permissions_db = user.permissions
            permissions_str = [
                permission.permission_name for permission in permissions_db
            ]
            permissions_enum = [
                PermissionsEnum(permission) for permission in permissions_str
            ]
            uwp = UsersWithPermissions(
                user_id=user.id,
                email=user.email,
                created_at=user.created_at,
                updated_at=user.updated_at,
                permissions=permissions_enum,
            )
            final_results.append(uwp)

        return final_results

    def get_user_email(self, user_id: int) -> str:
        return self._select_single_entry_from_relation(
            relation_name=Relations.USERS.value,
            columns=["email"],
            where_mappings={"id": user_id},
        )["email"]

    def pending_user_exists(self, email: str) -> bool:
        results = self._select_from_relation(
            relation_name=Relations.PENDING_USERS.value,
            columns=["id"],
            where_mappings={"email": email},
        )
        return len(results) > 0

    def create_pending_user(
        self, email: str, password_digest: str, validation_token: str
    ) -> str:
        return self._create_entry_in_table(
            table_name=Relations.PENDING_USERS.value,
            column_value_mappings={
                "email": email,
                "password_digest": password_digest,
                "validation_token": validation_token,
            },
        )

    def delete_user(self, user_id: int):
        self._delete_from_table(
            table_name=Relations.USERS.value,
            id_column_value=user_id,
            id_column_name="id",
        )

    def update_pending_user_validation_token(self, email: str, validation_token: str):
        self._update_entry_in_table(
            table_name=Relations.PENDING_USERS.value,
            entry_id=email,
            column_edit_mappings={"validation_token": validation_token},
            id_column_name="email",
        )

    def get_pending_user_with_token(self, validation_token: str) -> Optional[dict]:
        result = self._select_single_entry_from_relation(
            relation_name=Relations.PENDING_USERS.value,
            columns=["email", "password_digest"],
            where_mappings={"validation_token": validation_token},
        )
        return result

    def delete_pending_user(self, email: str):
        self._delete_from_table(
            table_name=Relations.PENDING_USERS.value,
            id_column_value=email,
            id_column_name="email",
        )

    def get_locality_id_by_location_id(self, location_id: int):
        return self._select_single_entry_from_relation(
            relation_name=Relations.LOCATIONS_EXPANDED.value,
            columns=["locality_id"],
            where_mappings={"id": location_id},
        )["locality_id"]

    @session_manager
    def get_location_by_id(self, location_id: int):
        query = Select(
            LocationExpanded,
        ).where(LocationExpanded.id == location_id)

        result = self.session.execute(query).scalar()

        if result is None:
            raise ValueError(f"Location with id {location_id} not found")

        return {
            "type": result.type,
            "location_id": result.id,
            "state_name": result.state_name,
            "state_iso": result.state_iso,
            "county_name": result.county_name,
            "county_fips": result.county_fips,
            "locality_name": result.locality_name,
            "display_name": ResultFormatter.get_expanded_display_name(result),
        }

    @session_manager
    def get_similar_agencies(
        self,
        name: str,
        location_id: Optional[int] = None,
    ) -> List[AgencyMatchResponseInnerDTO]:
        """
        Retrieve agencies similar to the query
        Optionally filtering based on the location id
        """
        query = Select(
            Agency,
            func.similarity(Agency.name, name),
        ).options(
            load_only(Agency.id, Agency.name, Agency.agency_type),
            selectinload(Agency.locations).load_only(
                LocationExpanded.state_name,
                LocationExpanded.county_name,
                LocationExpanded.locality_name,
                LocationExpanded.type,
            ),
        )
        if location_id is not None:
            query = query.where(
                Agency.locations.any(LocationExpanded.id == location_id)
            )
        query = query.order_by(func.similarity(Agency.name, name).desc()).limit(10)
        execute_results = self.session.execute(query).all()
        if len(execute_results) == 0:
            return []

        def result_to_dto(agency: Agency, similarity: float):
            locations = []
            for location in agency.locations:
                location_dto = AgencyMatchResponseLocationDTO(
                    state=location.state_name,
                    county=location.county_name,
                    locality=location.locality_name,
                    location_type=LocationType(location.type),
                )
                locations.append(location_dto)

            return AgencyMatchResponseInnerDTO(
                id=agency.id,
                name=agency.name,
                agency_type=AgencyType(agency.agency_type),
                similarity=similarity,
                locations=locations,
            )

        dto_results = []
        for result, similarity in execute_results:
            if similarity == 1:
                return [
                    result_to_dto(result, similarity),
                ]
            dto = result_to_dto(result, similarity)
            dto_results.append(dto)

        return dto_results

    def get_metrics(self):
        result = self.execute_raw_sql(
            """
            SELECT
                COUNT(*),
                'source_count' "Count Type"
            FROM
                DATA_SOURCES
            UNION
            SELECT
                COUNT(DISTINCT (AGENCY_ID)),
                'agency_count' "Count Type"
            FROM
                link_agencies_data_sources
            UNION
            SELECT
                COUNT(DISTINCT L.ID),
                'state_count' "Count Type"
            FROM
                LINK_AGENCIES_DATA_SOURCES LINK
                INNER JOIN AGENCIES A ON A.ID = LINK.AGENCY_ID
                LEFT JOIN LINK_AGENCIES_LOCATIONS LAL on A.ID = LAL.AGENCY_ID
                JOIN DEPENDENT_LOCATIONS DL ON LAL.LOCATION_ID = DL.DEPENDENT_LOCATION_ID
                JOIN LOCATIONS L ON L.ID = LAL.LOCATION_ID
                OR L.ID = DL.PARENT_LOCATION_ID
            WHERE
                L.TYPE = 'State'
            UNION
            SELECT
                COUNT(DISTINCT L.ID),
                'county_count' "Count Type"
            FROM
                LINK_AGENCIES_DATA_SOURCES LINK
                INNER JOIN AGENCIES A ON A.ID = LINK.AGENCY_ID
                LEFT JOIN LINK_AGENCIES_LOCATIONS LAL on A.ID = LAL.AGENCY_ID
                JOIN DEPENDENT_LOCATIONS DL ON LAL.LOCATION_ID = DL.DEPENDENT_LOCATION_ID
                JOIN LOCATIONS L ON L.ID = LAL.LOCATION_ID
                OR L.ID = DL.PARENT_LOCATION_ID
            WHERE
                L.TYPE = 'County'
	"""
        )
        d = {}
        for row in result:
            d[row["Count Type"]] = row["count"]
        return d

    @session_manager
    def get_record_types_and_categories(self):
        query = (
            select(RecordCategory)
            .options(selectinload(RecordCategory.record_types))
            .order_by(RecordCategory.id)
        )

        results: list[RecordCategory] = self.session.execute(query).scalars().all()

        record_types = []
        record_categories = []
        for result in results:
            record_cat_dict = {
                "id": result.id,
                "name": result.name,
                "description": result.description,
            }
            record_categories.append(record_cat_dict)
            for record_type in result.record_types:
                record_type_dict = {
                    "id": record_type.id,
                    "name": record_type.name,
                    "category_id": record_type.category_id,
                    "description": record_type.description,
                }
                record_types.append(record_type_dict)

        return {"record_types": record_types, "record_categories": record_categories}

    def reject_data_source(self, data_source_id: int, rejection_note: str):
        self.update_data_source(
            entry_id=data_source_id,
            column_edit_mappings={
                "approval_status": ApprovalStatus.REJECTED.value,
                "rejection_note": rejection_note,
            },
        )

    @session_manager
    def get_all(self, model: Type[Base]):

        def to_dict(instance):
            return {
                c.name: getattr(instance, c.name) for c in instance.__table__.columns
            }

        results = self.session.query(model).all()

        return [to_dict(result) for result in results]

    def get_record_type_cache(self, session: Session) -> dict[str, int]:
        d = {}
        for record_type in session.query(RecordType).all():
            d[record_type.name] = record_type.id
        return d

    @session_manager
    def add_data_sources_from_source_collector(
        self, data_sources: list[SourceCollectorPostRequestInnerDTO]
    ) -> list[SourceCollectorPostResponseInnerDTO]:
        record_type_cache = self.get_record_type_cache(self.session)
        results: list[SourceCollectorPostResponseInnerDTO] = []

        for data_source in data_sources:
            self.session.begin_nested()  # Starts a savepoint
            try:
                data_source_db = DataSource(
                    name=data_source.name,
                    description=data_source.description,
                    approval_status=ApprovalStatus.APPROVED.value,
                    source_url=data_source.source_url,
                    record_type_id=record_type_cache[data_source.record_type.value],
                    record_formats=data_source.record_formats,
                    data_portal_type=data_source.data_portal_type,
                    last_approval_editor=data_source.last_approval_editor,
                    supplying_entity=data_source.supplying_entity,
                    submission_notes="Auto-submitted from Source Collector",
                )
                self.session.add(data_source_db)
                self.session.flush()  # Execute the insert immediately
                for agency_id in data_source.agency_ids:
                    link = LinkAgencyDataSource(
                        data_source_id=data_source_db.id, agency_id=agency_id
                    )
                    self.session.add(link)

                self.session.flush()  # Execute the insert immediately

                # Success! Add to results
                dto = SourceCollectorPostResponseInnerDTO(
                    url=data_source.source_url,
                    status=DataSourceCreationResponse.SUCCESS,
                    data_source_id=data_source_db.id,
                )
                results.append(dto)

            except sqlalchemy.exc.IntegrityError as e:
                self.session.rollback()  # Roll back to the savepoint
                # Failure! Add to results
                dto = SourceCollectorPostResponseInnerDTO(
                    url=data_source.source_url,
                    status=DataSourceCreationResponse.FAILURE,
                    data_source_id=None,
                    error=str(e),
                )
                results.append(dto)
            else:
                self.session.commit()  # Release the savepoint

        return results

    @session_manager
    def update_location_by_id(self, location_id: int, dto: LocationPutDTO):
        try:
            location = (
                self.session.query(Location).filter(Location.id == location_id).one()
            )
            location.lat = dto.latitude
            location.lng = dto.longitude
        except sqlalchemy.exc.NoResultFound:
            raise LocationDoesNotExistError

    def refresh_materialized_view(self, view_name: str):
        self.session.execute_raw_sql(f"REFRESH MATERIALIZED VIEW {view_name};")

    def refresh_all_materialized_views(self):
        self.execute_raw_sql(
            """
        DO $$
        DECLARE
            rec RECORD;
        BEGIN
            FOR rec IN SELECT schemaname, matviewname FROM pg_matviews
            LOOP
                EXECUTE 'REFRESH MATERIALIZED VIEW ' || quote_ident(rec.schemaname) || '.' || quote_ident(rec.matviewname);
            END LOOP;
        END;
        $$;
        """
        )

    def get_map_localities(self):
        return self.execute_raw_sql(
            """
            SELECT 
                location_id,
                LOCALITY_NAME as name,
                county_name,
                JSON_BUILD_OBJECT(
                    'lat', lat,
                    'lng', lng
                ) AS coordinates,
                county_fips,
                state_iso,
                DATA_SOURCE_COUNT as source_count
            FROM
                PUBLIC.MAP_LOCALITIES
            """
        )

    def get_map_counties(self):
        return self.execute_raw_sql(
            """
            SELECT 
                location_id,
                county_name as name,
                state_iso,
                fips,
                DATA_SOURCE_COUNT as source_count
            FROM
                PUBLIC.MAP_COUNTIES
            """
        )

    def get_map_states(self):
        return self.execute_raw_sql(
            """
            SELECT 
                location_id,
                STATE_NAME as name,
                state_iso,
                DATA_SOURCE_COUNT as source_count
            FROM
                PUBLIC.MAP_STATES
            """
        )

    def get_data_source_count_by_location_type(self):
        return self.execute_raw_sql(
            """
            SELECT 
                localities,
                counties,
                states
            FROM
                PUBLIC.TOTAL_DATA_SOURCES_BY_LOCATION_TYPE
            """
        )[0]

    @session_manager
    def get_many_locations(
        self,
        page: int,
        has_coordinates: Optional[bool] = None,
        type_: Optional[LocationType] = None,
    ):
        query = select(Location)
        if has_coordinates is not None:
            if has_coordinates:
                query = query.where(
                    and_(
                        Location.lat != None,
                        Location.lng != None,
                    )
                )
            else:
                query = query.where(
                    and_(
                        Location.lat == None,
                        Location.lng == None,
                    )
                )
        if type_ is not None:
            query = query.where(Location.type == type_.value)

        # Select In Load
        for relationship in (
            "locality",
            "county",
            "state",
        ):
            query = query.options(selectinload(getattr(Location, relationship)))

        # Pagination
        query = query.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)

        raw_results = self.session.execute(query).scalars().all()
        results = []
        for raw_result in raw_results:
            result = {
                "location_id": raw_result.id,
                "type": raw_result.type,
                "state_name": (
                    raw_result.state.state_name
                    if raw_result.state is not None
                    else None
                ),
                "state_iso": (
                    raw_result.state.state_iso if raw_result.state is not None else None
                ),
                "county_name": (
                    raw_result.county.name if raw_result.county is not None else None
                ),
                "locality_name": (
                    raw_result.locality.name
                    if raw_result.locality is not None
                    else None
                ),
                "county_fips": (
                    raw_result.county.fips if raw_result.county is not None else None
                ),
                "coordinates": {
                    "lat": raw_result.lat,
                    "lng": raw_result.lng,
                },
            }
            results.append(result)

        return results

    @session_manager
    def add_to_notification_log(
        self,
        user_count: int,
        dt: Optional[datetime] = None,
    ):
        item = NotificationLog(
            user_count=user_count,
        )
        if dt is not None:
            item.created_at = dt
        self.session.add(item)

    @session_manager
    def get_metrics_followed_searches_breakdown(
        self, dto: MetricsFollowedSearchesBreakdownRequestDTO
    ):
        sortable_columns = GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS

        if dto.sort_by is not None:
            if dto.sort_by not in sortable_columns:
                raise BadRequest(
                    description=f"Invalid sort_by value: {dto.sort_by}; must be one of {sortable_columns}",
                )

        # Get last notification time
        last_notification_query = (
            select(NotificationLog.created_at)
            .order_by(NotificationLog.created_at.desc())
            .limit(1)
            .cte("last_notification")
        )

        last_notification = last_notification_query.c.created_at

        base_search_url = (
            f"{get_env_variable("VITE_VUE_APP_BASE_URL")}"
            f"/search/results?location_id="
        )

        def count_distinct(field, label):
            return func.count(func.distinct(field)).label(label)

        # Dependent Location CTE
        dlsq = union_all(
            select(
                Location.id.label("location_id"),
                DependentLocation.dependent_location_id,
            ).join(
                DependentLocation,
                Location.id == DependentLocation.parent_location_id,
                isouter=True,
            ),
            select(
                Location.id.label("location_id"),
                Location.id.label("dependent_location_id"),
            ),
        ).cte(name="dependent_locations_cte")

        def maybe_limit(column, limit_to_before_last_notification):
            """Maybe limit to before the last notification"""
            return (
                column < last_notification
                if limit_to_before_last_notification
                else True
            )

        def follower_count_subquery():
            link = LinkUserFollowedLocation
            return (
                select(
                    link.location_id.label("location_id"),
                    count_distinct(link.user_id, "total_count"),
                    count_distinct(
                        case(
                            (link.created_at < last_notification, link.user_id),
                        ),
                        "old_count",
                    ),
                )
                .join(dlsq, link.location_id == dlsq.c.dependent_location_id)
                .group_by(link.location_id)
                .cte("follow_counts")
            )

        def source_count_subquery():
            link = LinkLocationDataSourceView
            ds = DataSource
            return (
                select(
                    dlsq.c.location_id.label("location_id"),
                    count_distinct(ds.id, "total_count"),
                    count_distinct(
                        case((ds.created_at < last_notification, ds.id)),
                        "old_count",
                    ),
                )
                .join(link, link.location_id == dlsq.c.dependent_location_id)
                .join(ds, ds.id == link.data_source_id)
                .where(ds.approval_status == ApprovalStatus.APPROVED.value)
                .group_by(dlsq.c.location_id)
                .cte("source_counts")
            )

        def requests_col(request_status: RequestStatus, limit: bool, label: str):
            dr = DataRequest
            return count_distinct(
                case(
                    (
                        and_(
                            dr.request_status == request_status.value,
                            maybe_limit(dr.date_status_last_changed, limit),
                        ),
                        dr.id,
                    )
                ),
                label=f"{label}_count",
            )

        def requests_count_subquery():
            dr = DataRequest
            rs = RequestStatus
            link = LinkLocationDataRequest
            return (
                select(
                    dlsq.c.location_id.label("location_id"),
                    requests_col(rs.READY_TO_START, False, "total_approved"),
                    requests_col(rs.READY_TO_START, True, "old_approved"),
                    requests_col(rs.COMPLETE, False, "total_complete"),
                    requests_col(rs.COMPLETE, True, "old_complete"),
                )
                .join(link, link.location_id == dlsq.c.dependent_location_id)
                .join(dr, dr.id == link.data_request_id)
                .group_by(dlsq.c.location_id)
                .cte("request_counts")
            )

        def get_diff_v2(attr1, attr2, attribute_name):
            return (func.coalesce(attr1, 0) - func.coalesce(attr2, 0)).label(
                f"{attribute_name}_change"
            )

        follows = follower_count_subquery()
        diff_follows = get_diff_v2(
            follows.c.total_count, follows.c.old_count, "follower"
        )

        sources = source_count_subquery()
        diff_sources = get_diff_v2(sources.c.total_count, sources.c.old_count, "source")

        requests = requests_count_subquery()
        diff_approved_requests = get_diff_v2(
            requests.c.total_approved_count,
            requests.c.old_approved_count,
            "approved_requests",
        )
        diff_completed_requests = get_diff_v2(
            requests.c.total_complete_count,
            requests.c.old_complete_count,
            "completed_requests",
        )

        def coalesce(attr, label):
            return func.coalesce(attr, 0).label(label)

        final_query = (
            select(
                follows.c.location_id,
                LocationExpanded.full_display_name.label("location_name"),
                coalesce(follows.c.total_count, "follower_count"),
                diff_follows,
                coalesce(sources.c.total_count, "source_count"),
                diff_sources,
                coalesce(requests.c.total_approved_count, "approved_requests_count"),
                diff_approved_requests,
                coalesce(requests.c.total_complete_count, "completed_requests_count"),
                diff_completed_requests,
                func.concat(base_search_url, LocationExpanded.id).label("search_url"),
            )
            .select_from(follows)
            .join(LocationExpanded, follows.c.location_id == LocationExpanded.id)
        )

        for subquery in [sources, requests]:
            final_query = final_query.outerjoin(
                subquery,
                follows.c.location_id == subquery.c.location_id,
            )

        # The follower count must be nonzero
        final_query = final_query.where(
            follows.c.total_count > 0,
        )

        if dto.sort_by is not None:
            final_query = final_query.order_by(
                text(f"{dto.sort_by} {dto.sort_order.value}")
            )
        final_query = final_query.limit(100).offset((dto.page - 1) * 100)

        raw_results = self.session.execute(final_query).all()

        results = []
        for result in raw_results:
            d = {
                "location_name": result.location_name,
                "location_id": result.location_id,
                "follower_count": result.follower_count,
                "follower_change": result.follower_change,
                "source_count": result.source_count,
                "source_change": result.source_change,
                "approved_requests_count": result.approved_requests_count,
                "approved_requests_change": result.approved_requests_change,
                "completed_requests_count": result.completed_requests_count,
                "completed_requests_change": result.completed_requests_change,
                "search_url": result.search_url,
            }
            results.append(d)

        return results

    @session_manager
    def get_metrics_followed_searches_aggregate(self):
        subquery_latest_notification = (
            select(NotificationLog.created_at.label("last_notification"))
            .order_by(NotificationLog.created_at.desc())
            .limit(1)
            .scalar_subquery()
        )

        statement = select(
            func.count(func.distinct(LinkUserFollowedLocation.user_id)).label(
                "total_followers"
            ),
            func.count(LinkUserFollowedLocation.location_id).label("location_count"),
            subquery_latest_notification.label("last_notification"),
        )

        result = self.session.execute(statement).one()

        return {
            "total_followers": result.total_followers,
            "total_followed_searches": result.location_count,
            "last_notification_date": result.last_notification.strftime("%Y-%m-%d"),
        }
