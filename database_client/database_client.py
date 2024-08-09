import json
from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Any, List
import uuid

import psycopg2
from psycopg2 import sql

from database_client.dynamic_query_constructor import DynamicQueryConstructor
from database_client.enums import ExternalAccountTypeEnum
from middleware.custom_exceptions import (
    UserNotFoundError,
    TokenNotFoundError,
    AccessTokenNotFoundError,
)
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

    def __init__(self, cursor: psycopg2.extensions.cursor):
        self.cursor = cursor

    def add_new_user(self, email: str, password_digest: str):
        """
        Adds a new user to the database.
        :param email:
        :param password_digest:
        :return:
        """
        query = sql.SQL(
            "insert into users (email, password_digest) values ({}, {})"
        ).format(
            sql.Literal(email),
            sql.Literal(password_digest),
        )
        self.cursor.execute(query)

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
        query = sql.SQL(
            "update users set password_digest = {} where email = {}"
        ).format(
            sql.Literal(password_digest),
            sql.Literal(email),
        )
        self.cursor.execute(query)

    ResetTokenInfo = namedtuple("ResetTokenInfo", ["id", "email", "create_date"])

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

    SessionTokenInfo = namedtuple(
        "SessionTokenInfo", ["id", "email", "expiration_date"]
    )

    def get_session_token_info(self, api_key: str) -> Optional[SessionTokenInfo]:
        """
        Checks if a session token exists in the database and retrieves the associated user data.

        :param api_key: The session token to check.
        :return: SessionTokenInfo if the token exists; otherwise, None.
        """
        query = sql.SQL(
            "select id, email, expiration_date from session_tokens where token = {}"
        ).format(sql.Literal(api_key))
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self.SessionTokenInfo(id=row[0], email=row[1], expiration_date=row[2])

    RoleInfo = namedtuple("RoleInfo", ["id", "role"])

    def get_role_by_api_key(self, api_key: str) -> Optional[RoleInfo]:
        """
        Get role and user id for a given api key
        :param api_key: The api key to check.
        :return: RoleInfo if the token exists; otherwise, None.
        """
        query = sql.SQL("select id, role from users where api_key = {}").format(
            sql.Literal(api_key)
        )
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self.RoleInfo(id=row[0], role=row[1])

    def get_role_by_email(self, email: str) -> RoleInfo:
        """
        Retrieves a user's role from the database using a given email.

        :param email: User's email.
        :raises UserNotFoundError: If no user is found.
        :return: RoleInfo namedtuple containing the user's role.
        """
        query = sql.SQL("select role from users where email = {}")
        query = query.format(sql.Literal(email))
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        if len(results) == 0:
            raise UserNotFoundError(email)

        return self.RoleInfo(id=None, role=results[0])

    def update_user_api_key(self, api_key: str, user_id: int):
        """
        Update the api key for a user
        :param api_key: The api key to check.
        :param user_id: The user id to update.
        """
        query = sql.SQL("update users set api_key = {} where id = {}")
        query = query.format(sql.Literal(api_key), sql.Literal(user_id))

        self.cursor.execute(query)

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
        sql_query = DynamicQueryConstructor.create_data_source_update_query(
            data, data_source_id
        )
        self.cursor.execute(sql_query)

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
        self, id: str, broken_as_of: str, last_cached: str
    ) -> None:
        """
        Updates the data_sources table setting the url_status to 'broken' for a given id.

        :param id: The airtable_uid of the data source.
        :param broken_as_of: The date when the source was identified as broken.
        :param last_cached: The last cached date of the data source.
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
        sql_query = "UPDATE data_sources_archive_info SET last_cached = %s WHERE airtable_uid = %s"
        self.cursor.execute(sql_query, (last_cached, id))

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

    def add_new_access_token(self, token: str, expiration: datetime) -> None:
        """Inserts a new access token into the database."""
        query = sql.SQL(
            "insert into access_tokens (token, expiration_date) values ({token}, {expiration})"
        ).format(
            token=sql.Literal(token),
            expiration=sql.Literal(expiration),
        )
        self.cursor.execute(query)

    UserInfo = namedtuple("UserInfo", ["id", "password_digest", "api_key", "email"])

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

    def get_user_info_by_external_account_id(
            self,
            external_account_id: str,
            external_account_type: ExternalAccountTypeEnum
    ) -> UserInfo:
        query = sql.SQL("""
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
        """).format(
            external_account_identifier=sql.Literal(external_account_id),
            external_account_type=sql.Literal(external_account_type.value)
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

    def add_new_session_token(self, session_token, email: str, expiration) -> None:
        """
        Inserts a session token into the database.

        :param session_token: The session token.
        :param email: User's email.
        :param expiration: The session token's expiration.
        """
        query = sql.SQL(
            "insert into session_tokens (token, email, expiration_date) values ({token}, {email}, {expiration})"
        ).format(
            token=sql.Literal(session_token),
            email=sql.Literal(email),
            expiration=sql.Literal(expiration),
        )
        self.cursor.execute(query)

    SessionTokenUserData = namedtuple("SessionTokenUserData", ["id", "email"])

    def delete_session_token(self, old_token: str) -> None:
        """
        Deletes a session token from the database.

        :param old_token: The session token.
        """
        query = sql.SQL("delete from session_tokens where token = {token}").format(
            token=sql.Literal(old_token)
        )
        self.cursor.execute(query)

    AccessToken = namedtuple("AccessToken", ["id", "token"])

    def get_access_token(self, api_key: str) -> AccessToken:
        """
        Retrieves an access token from the database.

        :param api_key: The access token.
        :raise AccessTokenNotFoundError: If the access token is not found.
        :returns: AccessToken namedtuple with the ID and the access token.
        """
        query = sql.SQL(
            "select id, token from access_tokens where token = {token}"
        ).format(token=sql.Literal(api_key))
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        if not results:
            raise AccessTokenNotFoundError("Access token not found")
        return self.AccessToken(id=results[0], token=results[1])

    def delete_expired_access_tokens(self) -> None:
        """Deletes all expired access tokens from the database."""
        self.cursor.execute("delete from access_tokens where expiration_date < NOW()")

    TypeaheadSuggestions = namedtuple(
        "TypeaheadSuggestions", ["display_name", "type", "state", "county", "locality"]
    )
    def get_typeahead_suggestions(self, search_term: str) -> List[TypeaheadSuggestions]:
        """
        Returns a list of data sources that match the search query.

        :param search_term: The search query.
        :return: List of data sources that match the search query.
        """
        query = DynamicQueryConstructor.generate_new_typeahead_suggestion_query(search_term)
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
            state=state, record_categories=record_categories, county=county, locality=locality
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

    def link_external_account(
            self,
            user_id: str,
            external_account_id: str,
            external_account_type: ExternalAccountTypeEnum):
        query = sql.SQL("""
            INSERT INTO external_accounts (user_id, account_type, account_identifier) 
            VALUES ({user_id}, {account_type}, {account_identifier});
        """).format(
            user_id=sql.Literal(user_id),
            account_type=sql.Literal(external_account_type.value),
            account_identifier=sql.Literal(external_account_id),
        )
        self.cursor.execute(query)

