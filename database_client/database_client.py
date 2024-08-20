import json
from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Optional, Any, List
import uuid

import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor, DictRow

from database_client.dynamic_query_constructor import DynamicQueryConstructor
from database_client.enums import (
    ExternalAccountTypeEnum,
    RelationRoleEnum,
    ColumnPermissionEnum,
)
from middleware.custom_exceptions import (
    UserNotFoundError,
    TokenNotFoundError,
    AccessTokenNotFoundError,
)
from middleware.enums import PermissionsEnum
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
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


QUICK_SEARCH_SQL = """
    SELECT
        data_sources.airtable_uid,
        data_sources.name AS data_source_name,
        data_sources.description,
        data_sources.record_type,
        data_sources.source_url,
        data_sources.record_format,
        data_sources.coverage_start,
        data_sources.coverage_end,
        data_sources.agency_supplied,
        agencies.name AS agency_name,
        agencies.municipality,
        agencies.state_iso
    FROM
        agency_source_link
    INNER JOIN
        data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
    INNER JOIN
        agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
    INNER JOIN
        state_names ON agencies.state_iso = state_names.state_iso
    WHERE
        (data_sources.name ILIKE '%{0}%' OR data_sources.description ILIKE '%{0}%' OR data_sources.record_type ILIKE '%{0}%' OR data_sources.tags ILIKE '%{0}%') 
        AND (agencies.county_name ILIKE '%{1}%' OR substr(agencies.county_name,3,length(agencies.county_name)-4) || ' County' ILIKE '%{1}%' 
            OR agencies.state_iso ILIKE '%{1}%' OR agencies.municipality ILIKE '%{1}%' OR agencies.agency_type ILIKE '%{1}%' OR agencies.jurisdiction_type ILIKE '%{1}%' 
            OR agencies.name ILIKE '%{1}%' OR state_names.state_name ILIKE '%{1}%')
        AND data_sources.approval_status = 'approved'
        AND data_sources.url_status not in ('broken', 'none found')

"""


class DatabaseClient:

    def __init__(self):
        self.connection = initialize_psycopg2_connection()
        self.cursor = None

    def cursor_manager(method):
        """Decorator method for managing a cursor object.
        The cursor is closed after the method concludes its execution.

        :param method: The method being called upon.
        :raises e: If an error occurs, rollback the current transaction.
        :return: result of the method.
        """

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Open a new cursor
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
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

    def close(self):
        self.connection.close()

    @cursor_manager
    def execute_raw_sql(
        self, query: str, vars: Optional[tuple] = None
    ) -> Optional[list[DictRow]]:
        """Executes an SQL query passed to the function.

        :param query: The SQL query to execute.
        :param vars: A tuple of variables to replace placeholders in the SQL query, defaults to None
        :return: A list of DictRow objects when there are multiple results, a single DictRow object if there is one result, or None if there are no results.
        """
        self.cursor.execute(query, vars)
        try:
            results = self.cursor.fetchall()
        except psycopg2.ProgrammingError:
            return None

        if len(results) == 0:
            return None
        return results

    @cursor_manager
    def add_new_user(self, email: str, password_digest: str) -> Optional[int]:
        """
        Adds a new user to the database.
        :param email:
        :param password_digest:
        :return:
        """
        query = sql.SQL(
            "insert into users (email, password_digest) values ({}, {}) returning id"
        ).format(
            sql.Literal(email),
            sql.Literal(password_digest),
        )
        self.cursor.execute(query)
        if self.cursor.rowcount == 0:
            return None
        return self.cursor.fetchone()[0]

    @cursor_manager
    def get_user_id(self, email: str) -> Optional[int]:
        """
        Gets the ID of a user in the database based on their email.
        :param email:
        :return:
        """
        query = sql.SQL("select id from users where email = {}").format(
            sql.Literal(email)
        )
        self.cursor.execute(query)
        if self.cursor.rowcount == 0:
            return None
        return self.cursor.fetchone()[0]

    def set_user_password_digest(self, email: str, password_digest: str):
        """
        Updates the password digest for a user in the database.
        :param email:
        :param password_digest:
        :return:
        """
        self._update_entry_in_table(
            table_name="users",
            entry_id=email,
            column_edit_mappings={"password_digest": password_digest},
            id_column_name="email"
        )

    ResetTokenInfo = namedtuple("ResetTokenInfo", ["id", "email", "create_date"])

    @cursor_manager
    def get_reset_token_info(self, token: str) -> Optional[ResetTokenInfo]:
        """
        Checks if a reset token exists in the database and retrieves the associated user data.

        :param token: The reset token to check.
        :return: ResetTokenInfo if the token exists; otherwise, None.
        """
        query = sql.SQL(
            "select id, email, create_date from reset_tokens where token = {}"
        ).format(sql.Literal(token))
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self.ResetTokenInfo(id=row[0], email=row[1], create_date=row[2])

    @cursor_manager
    def add_reset_token(self, email: str, token: str):
        """
        Inserts a new reset token into the database for a specified email.

        :param email: The email to associate with the reset token.
        :param token: The reset token to add.
        """
        query = sql.SQL(
            "insert into reset_tokens (email, token) values ({}, {})"
        ).format(sql.Literal(email), sql.Literal(token))
        self.cursor.execute(query)

    @cursor_manager
    def delete_reset_token(self, email: str, token: str):
        """
        Deletes a reset token from the database for a specified email.

        :param email: The email associated with the reset token to delete.
        :param token: The reset token to delete.
        """
        query = sql.SQL(
            "delete from reset_tokens where email = {} and token = {}"
        ).format(sql.Literal(email), sql.Literal(token))
        self.cursor.execute(query)

    UserIdentifiers = namedtuple("UserIdentifiers", ["id", "email"])

    @cursor_manager
    def get_user_by_api_key(self, api_key: str) -> Optional[UserIdentifiers]:
        """
        Get user id for a given api key
        :param api_key: The api key to check.
        :return: RoleInfo if the token exists; otherwise, None.
        """
        query = sql.SQL("select id, email from users where api_key = {}").format(
            sql.Literal(api_key)
        )
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self.UserIdentifiers(id=row[0], email=row[1])

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

    @cursor_manager
    def get_data_source_by_id(self, data_source_id: str) -> Optional[tuple[Any, ...]]:
        """
        Get a data source by its ID, including related agency information from the database.
        :param data_source_id: The unique identifier for the data source.
        :return: A dictionary containing the data source and its related agency details. None if not found.
        """
        sql_query = DynamicQueryConstructor.build_data_source_by_id_results_query()
        self.cursor.execute(
            sql_query,
            (data_source_id,),
        )
        result = self.cursor.fetchone()
        # NOTE: Very big tuple, perhaps very long NamedTuple to be implemented later
        return result

    @cursor_manager
    def get_approved_data_sources(self) -> list[tuple[Any, ...]]:
        """
        Fetches all approved data sources and their related agency information from the database.

        :param columns: List of column names to use in the SELECT statement.
        :return: A list of tuples, each containing details of a data source and its related agency.
        """

        sql_query = DynamicQueryConstructor.build_get_approved_data_sources_query()

        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()
        # NOTE: Very big tuple, perhaps very long NamedTuple to be implemented later
        return results

    @cursor_manager
    def get_needs_identification_data_sources(self) -> list[tuple[Any, ...]]:
        """
        Returns a list of data sources that need identification from the database.

        :param columns: List of column names to use in the SELECT statement.
        :return: A list of tuples, each containing details of a data source.
        """
        sql_query = (
            DynamicQueryConstructor.build_needs_identification_data_source_query()
        )
        self.cursor.execute(sql_query)
        return self.cursor.fetchall()

    @cursor_manager
    def add_new_data_source(self, data: dict) -> None:
        """
        Processes a request to add a new data source.

        :param data: A dictionary containing the updated data source details.
        """
        sql_query = DynamicQueryConstructor.create_new_data_source_query(data)
        self.cursor.execute(sql_query)

    def update_data_source(self, data: dict, data_source_id: str) -> None:
        """
        Processes a request to update a data source.

        :param data_source_id: The data source's ID.
        :param data: A dictionary containing the data source details.
        """
        self._update_entry_in_table(
            table_name="data_sources",
            entry_id=data_source_id,
            column_edit_mappings=data,
            id_column_name="airtable_uid"
        )


    MapInfo = namedtuple(
        "MapInfo",
        [
            "data_source_id",
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

    @cursor_manager
    def get_data_sources_for_map(self) -> list[MapInfo]:
        """
        Returns a list of data sources with relevant info for the map from the database.

        :return: A list of MapInfo namedtuples, each containing details of a data source.
        """
        sql_query = """
            SELECT
                data_sources.airtable_uid as data_source_id,
                data_sources.name,
                agencies.airtable_uid as agency_id,
                agencies.submitted_name as agency_name,
                agencies.state_iso,
                agencies.municipality,
                agencies.county_name,
                data_sources.record_type,
                agencies.lat,
                agencies.lng
            FROM
                agency_source_link
            INNER JOIN
                data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
            INNER JOIN
                agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
            WHERE
                data_sources.approval_status = 'approved'
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        return [self.MapInfo(*result) for result in results]

    @cursor_manager
    def get_agencies_from_page(self, page: int) -> list[tuple[Any, ...]]:
        """
        Returns a list of up to 1000 agencies from the database from a given page.

        :param page: The page number to pull the agencies from.
        :return: A list of agency tuples.
        """
        offset = self.get_offset(page)
        sql_query = """
            SELECT 
                name,
                homepage_url,
                count_data_sources,
                agency_type,
                multi_agency,
                submitted_name,
                jurisdiction_type,
                state_iso,
                municipality,
                zip_code,
                county_fips,
                county_name,
                lat,
                lng,
                data_sources,
                no_web_presence,
                airtable_agency_last_modified,
                data_sources_last_updated,
                approved,
                rejection_reason,
                last_approval_editor,
                agency_created,
                county_airtable_uid,
                defunct_year,
                airtable_uid
            FROM agencies where approved = 'TRUE' limit 1000 offset %s
        """
        self.cursor.execute(
            sql_query,
            (offset,),
        )
        results = self.cursor.fetchall()
        return results

    @staticmethod
    def get_offset(page: int) -> int:
        """
        Calculates the offset value for pagination based on the given page number.
        Args:
            page (int): The page number for which the offset is to be calculated.
        Returns:
            int: The calculated offset value.
        Example:
            >>> get_offset(3)
            2000
        """
        return (page - 1) * 1000

    ArchiveInfo = namedtuple(
        "ArchiveInfo",
        ["id", "url", "update_frequency", "last_cached", "broken_url_as_of"],
    )

    @cursor_manager
    def get_data_sources_to_archive(self) -> list[ArchiveInfo]:
        """
        Pulls data sources to be archived by the automatic archives script.

        A data source is selected for archival if:
        The data source has been approved
        AND (the data source has not been archived previously OR the data source is updated regularly)
        AND the source url is not broken
        AND the source url is not null.

        :return: A list of ArchiveInfo namedtuples, each containing archive details of a data source.
        """
        sql_query = """
        SELECT
            data_sources.airtable_uid,
            source_url,
            update_frequency,
            last_cached,
            broken_source_url_as_of
        FROM
            data_sources
        INNER JOIN
            data_sources_archive_info
        ON
            data_sources.airtable_uid = data_sources_archive_info.airtable_uid
        WHERE 
            approval_status = 'approved' AND (last_cached IS NULL OR update_frequency IS NOT NULL) AND broken_source_url_as_of IS NULL AND url_status <> 'broken' AND source_url IS NOT NULL
        """
        self.cursor.execute(sql_query)
        data_sources = self.cursor.fetchall()

        results = [
            self.ArchiveInfo(
                id=row[0],
                url=row[1],
                update_frequency=row[2],
                last_cached=row[3],
                broken_url_as_of=row[4],
            )
            for row in data_sources
        ]

        return results

    def update_url_status_to_broken(
        self, id: str, broken_as_of: str
    ) -> None:
        """
        Updates the data_sources table setting the url_status to 'broken' for a given id.

        :param id: The airtable_uid of the data source.
        :param broken_as_of: The date when the source was identified as broken.
        """
        self.update_data_source(
            data_source_id=id,
            data={
                "url_status": "broken",
                "broken_source_url_as_of": broken_as_of,
            },
        )

    def update_last_cached(self, id: str, last_cached: str) -> None:
        """
        Updates the last_cached field in the data_sources_archive_info table for a given id.

        :param id: The airtable_uid of the data source.
        :param last_cached: The last cached date to be updated.
        """
        self._update_entry_in_table(
            table_name="data_sources_archive_info",
            entry_id=id,
            column_edit_mappings={"last_cached": last_cached},
            id_column_name="airtable_uid"
        )

    QuickSearchResult = namedtuple(
        "QuickSearchResults",
        [
            "id",
            "data_source_name",
            "description",
            "record_type",
            "url",
            "format",
            "coverage_start",
            "coverage_end",
            "agency_supplied",
            "agency_name",
            "municipality",
            "state",
        ],
    )

    @cursor_manager
    def get_quick_search_results(
        self, search: str, location: str
    ) -> Optional[list[QuickSearchResult]]:
        """
        Executes the quick search SQL query with search and location terms.

        :param search: The search term entered by the user.
        :param location: The location term entered by the user.
        :return: A list of QuickSearchResult namedtuples, each containing information of a data source resulting from the search. None if nothing is found.
        """
        print(f"Query parameters: '%{search}%', '%{location}%'")
        sql_query = QUICK_SEARCH_SQL.format(search, location)

        self.cursor.execute(sql_query)
        data_sources = self.cursor.fetchall()

        results = [
            self.QuickSearchResult(
                id=row[0],
                data_source_name=row[1],
                description=row[2],
                record_type=row[3],
                url=row[4],
                format=row[5],
                coverage_start=row[6],
                coverage_end=row[7],
                agency_supplied=row[8],
                agency_name=row[9],
                municipality=row[10],
                state=row[11],
            )
            for row in data_sources
        ]

        return results

    DataSourceMatches = namedtuple("DataSourceMatches", ["converted", "ids"])
    SearchParameters = namedtuple("SearchParameters", ["search", "location"])

    @cursor_manager
    def add_quick_search_log(
        self,
        data_sources_count: int,
        processed_data_source_matches: DataSourceMatches,
        processed_search_parameters: SearchParameters,
    ) -> None:
        """
        Logs a quick search query in the database.

        :param data_sources_count: Number of data sources in the search results.
        :param processed_data_source_matches: DataSourceMatches namedtuple with a list of data sources processed so that the dates are converted to strings, and a list of resulting IDs.
        :param processed_search_parameters: SearchParameters namedtuple with the search and location parameters
        """
        query_results = json.dumps(processed_data_source_matches.ids).replace("'", "")
        sql_query = """
            INSERT INTO quick_search_query_logs (search, location, results, result_count) 
            VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(
            sql_query,
            (
                processed_search_parameters.search,
                processed_search_parameters.location,
                query_results,
                data_sources_count,
            ),
        )

    UserInfo = namedtuple("UserInfo", ["id", "password_digest", "api_key", "email"])

    @cursor_manager
    def get_user_info(self, email: str) -> UserInfo:
        """
        Retrieves user data by email.

        :param email: User's email.
        :raise UserNotFoundError: If no user is found.
        :return: UserInfo namedtuple containing the user's information.
        """
        query = sql.SQL(
            "select id, password_digest, api_key, email from users where email = {email}"
        ).format(email=sql.Literal(email))
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        if results is None:
            raise UserNotFoundError(email)

        return self.UserInfo(
            id=results[0],
            password_digest=results[1],
            api_key=results[2],
            email=results[3],
        )

    @cursor_manager
    def get_user_info_by_external_account_id(
        self, external_account_id: str, external_account_type: ExternalAccountTypeEnum
    ) -> UserInfo:
        query = sql.SQL(
            """
            SELECT 
                u.id,
                u.email,
                u.password_digest,
                u.api_key
            FROM 
                users u
            INNER JOIN 
                external_accounts ea ON u.id = ea.user_id
            WHERE 
                ea.account_identifier = {external_account_identifier}
                and ea.account_type = {external_account_type}
        """
        ).format(
            external_account_identifier=sql.Literal(external_account_id),
            external_account_type=sql.Literal(external_account_type.value),
        )
        self.cursor.execute(query)

        results = self.cursor.fetchone()
        if results is None:
            raise UserNotFoundError(external_account_id)

        return self.UserInfo(
            id=results["id"],
            password_digest=results["password_digest"],
            api_key=results["api_key"],
            email=results["email"],
        )

    TypeaheadSuggestions = namedtuple(
        "TypeaheadSuggestions", ["display_name", "type", "state", "county", "locality"]
    )

    @cursor_manager
    def get_typeahead_suggestions(self, search_term: str) -> List[TypeaheadSuggestions]:
        """
        Returns a list of data sources that match the search query.

        :param search_term: The search query.
        :return: List of data sources that match the search query.
        """
        query = DynamicQueryConstructor.generate_new_typeahead_suggestion_query(
            search_term
        )
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return [
            self.TypeaheadSuggestions(
                display_name=row[1],
                type=row[2],
                state=row[3],
                county=row[4],
                locality=row[5],
            )
            for row in results
        ]

    @cursor_manager
    def search_with_location_and_record_type(
        self,
        state: str,
        record_categories: Optional[list[RecordCategories]] = None,
        county: Optional[str] = None,
        locality: Optional[str] = None,
    ) -> List[QuickSearchResult]:
        """
        Searches for data sources in the database.

        :param state: The state to search for data sources in.
        :param record_categories: The types of data sources to search for. If None, all data sources will be searched for.
        :param county: The county to search for data sources in. If None, all data sources will be searched for.
        :param locality: The locality to search for data sources in. If None, all data sources will be searched for.
        :return: A list of QuickSearchResult objects.
        """
        query = DynamicQueryConstructor.create_search_query(
            state=state,
            record_categories=record_categories,
            county=county,
            locality=locality,
        )
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [
            self.QuickSearchResult(
                id=row[0],
                data_source_name=row[1],
                description=row[2],
                record_type=row[3],
                url=row[4],
                format=row[5],
                coverage_start=row[6],
                coverage_end=row[7],
                agency_supplied=row[8],
                agency_name=row[9],
                municipality=row[10],
                state=row[11],
            )
            for row in results
        ]

    @cursor_manager
    def link_external_account(
        self,
        user_id: str,
        external_account_id: str,
        external_account_type: ExternalAccountTypeEnum,
    ):
        query = sql.SQL(
            """
            INSERT INTO external_accounts (user_id, account_type, account_identifier) 
            VALUES ({user_id}, {account_type}, {account_identifier});
        """
        ).format(
            user_id=sql.Literal(user_id),
            account_type=sql.Literal(external_account_type.value),
            account_identifier=sql.Literal(external_account_id),
        )
        self.cursor.execute(query)

    @cursor_manager
    def add_user_permission(self, user_email: str, permission: PermissionsEnum):
        query = sql.SQL(
            """
            INSERT INTO user_permissions (user_id, permission_id) 
            VALUES (
                (SELECT id FROM users WHERE email = {email}), 
                (SELECT permission_id FROM permissions WHERE permission_name = {permission})
            );
        """
        ).format(
            email=sql.Literal(user_email),
            permission=sql.Literal(permission.value),
        )
        self.cursor.execute(query)

    @cursor_manager
    def remove_user_permission(self, user_email: str, permission: PermissionsEnum):
        query = sql.SQL(
            """
            DELETE FROM user_permissions
            WHERE user_id = (SELECT id FROM users WHERE email = {email})
            AND permission_id = (SELECT permission_id FROM permissions WHERE permission_name = {permission});
        """
        ).format(
            email=sql.Literal(user_email),
            permission=sql.Literal(permission.value),
        )
        self.cursor.execute(query)

    @cursor_manager
    def get_user_permissions(self, user_id: str) -> List[PermissionsEnum]:
        query = sql.SQL(
            """
            SELECT p.permission_name
            FROM 
            user_permissions up
            INNER JOIN permissions p on up.permission_id = p.permission_id
            where up.user_id = {user_id}
        """
        ).format(
            user_id=sql.Literal(user_id),
        )
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [PermissionsEnum(row[0]) for row in results]

    @cursor_manager
    def get_permitted_columns(
        self,
        relation: str,
        role: RelationRoleEnum,
        column_permission: ColumnPermissionEnum,
    ) -> list[str]:
        """
        Gets permitted columns for a given relation, role, and permission type
        :param relation:
        :param role:
        :param column_permission:
        :return:
        """
        # If the column permission is READ, return also WRITE values, which are assumed to include READ
        if column_permission == ColumnPermissionEnum.READ:
            column_permissions = (
                ColumnPermissionEnum.READ.value,
                ColumnPermissionEnum.WRITE.value,
            )
        else:
            column_permissions = (column_permission.value,)

        query = sql.SQL(
            """
         SELECT rc.associated_column
            FROM column_permission cp
            INNER JOIN relation_column rc on rc.id = cp.rc_id
            WHERE rc.relation = {relation}
            and cp.relation_role = {relation_role}
            and cp.access_permission in {column_permissions}
        """
        ).format(
            relation=sql.Literal(relation),
            relation_role=sql.Literal(role.value),
            column_permissions=sql.Literal(column_permissions),
        )
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [row[0] for row in results]

    @cursor_manager
    def _update_entry_in_table(
        self,
        table_name: str,
        entry_id: Any,
        column_edit_mappings: dict[str, str],
        id_column_name: str = "id",
    ):
        """
        Updates a specific entry in a table in the database.

        :param table_name: The name of the table to update.
        :param entry_id: The ID of the entry to update.
        :param column_edit_mappings: A dictionary mapping column names to their new values.
        """
        query = DynamicQueryConstructor.create_update_query(
            table_name, entry_id, column_edit_mappings, id_column_name
        )
        self.cursor.execute(query)
