from collections import namedtuple
from datetime import datetime
from http import HTTPStatus
from typing import Union, Optional, Any
import uuid

import psycopg2

from middleware.custom_exceptions import UserNotFoundError, TokenNotFoundError, AccessTokenNotFoundError


RESTRICTED_COLUMNS = [
    "rejection_note",
    "data_source_request",
    "approval_status",
    "airtable_uid",
    "airtable_source_last_modified",
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
        (data_sources.name LIKE '%{0}%' OR data_sources.description LIKE '%{0}%' OR data_sources.record_type LIKE '%{0}%' OR data_sources.tags LIKE '%{0}%') 
        AND (agencies.county_name LIKE '%{1}%' OR substr(agencies.county_name,3,length(agencies.county_name)-4) || ' County' LIKE '%{1}%' 
            OR agencies.state_iso LIKE '%{1}%' OR agencies.municipality LIKE '%{1}%' OR agencies.agency_type LIKE '%{1}%' OR agencies.jurisdiction_type LIKE '%{1}%' 
            OR agencies.name LIKE '%{1}%' OR state_names.state_name LIKE '%{1}%')
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
        self.cursor.execute(
            f"insert into users (email, password_digest) values (%s, %s)",
            (email, password_digest),
        )

    def get_user_id(self, email: str) -> Optional[int]:
        """
        Gets the ID of a user in the database based on their email.
        :param email:
        :return:
        """
        self.cursor.execute(f"select id from users where email = %s", (email,))
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
        self.cursor.execute(
            f"update users set password_digest = %s where email = %s",
            (password_digest, email),
        )

    ResetTokenInfo = namedtuple("ResetTokenInfo", ["id", "email", "create_date"])

    def get_reset_token_info(self, token: str) -> Optional[ResetTokenInfo]:
        """
        Checks if a reset token exists in the database and retrieves the associated user data.

        :param token: The reset token to check.
        :return: ResetTokenInfo if the token exists; otherwise, None.
        """
        self.cursor.execute(
            f"select id, email, create_date from reset_tokens where token = %s",
            (token,),
        )
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
        self.cursor.execute(
            f"insert into reset_tokens (email, token) values (%s, %s)", (email, token)
        )

    def delete_reset_token(self, email: str, token: str):
        """
        Deletes a reset token from the database for a specified email.

        :param email: The email associated with the reset token to delete.
        :param token: The reset token to delete.
        """
        self.cursor.execute(
            f"delete from reset_tokens where email = %s and token = %s", (email, token)
        )

    SessionTokenInfo = namedtuple("SessionTokenInfo", ["email", "expiration_date"])

    def get_session_token_info(self, api_key: str) -> Optional[SessionTokenInfo]:
        """
        Checks if a session token exists in the database and retrieves the associated user data.

        :param api_key: The session token to check.
        :return: SessionTokenInfo if the token exists; otherwise, None.
        """
        self.cursor.execute(
            f"select email, expiration_date from session_tokens where token = %s",
            (api_key,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self.SessionTokenInfo(email=row[0], expiration_date=row[1])

    RoleInfo = namedtuple("RoleInfo", ["id", "role"])

    def get_role_by_api_key(self, api_key: str) -> Optional[RoleInfo]:
        """
        Get role and user id for a given api key
        :param api_key: The api key to check.
        :return: RoleInfo if the token exists; otherwise, None.
        """
        self.cursor.execute(
            f"select id, role from users where api_key = %s",
            (api_key,),
        )
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
        self.cursor.execute(f"select role from users where email = %s", (email,))
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
        self.cursor.execute(
            f"update users set api_key = %s where id = %s",
            (api_key, user_id),
        )

    def get_data_source_by_id(
        self, columns: list[str], data_source_id: str
    ) -> Optional[tuple[Any, ...]]:
        """
        Get a data source by its ID, including related agency information from the database.

        :param data_source_id: The unique identifier for the data source.
        :param columns: List of column names to use in the SELECT statement.
        :return: A dictionary containing the data source and its related agency details. None if not found.
        """
        joined_column_names = ", ".join(columns)
        sql_query = """
            SELECT
                %s
            FROM
                agency_source_link
            INNER JOIN
                data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
            INNER JOIN
                agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
            WHERE
                data_sources.approval_status = 'approved' AND data_sources.airtable_uid = %s
        """

        self.cursor.execute(
            sql_query,
            (
                joined_column_names,
                data_source_id,
            ),
        )
        result = self.cursor.fetchone()
        # NOTE: Very big tuple, perhaps very long NamedTuple to be implemented later
        return result

    def get_approved_data_sources(self, columns: list[str]) -> list[tuple[Any, ...]]:
        """
        Fetches all approved data sources and their related agency information from the database.

        :param columns: List of column names to use in the SELECT statement.
        :return: A list of tuples, each containing details of a data source and its related agency.
        """
        joined_column_names = ", ".join(columns)
        sql_query = """
            SELECT
                %s
            FROM
                agency_source_link
            INNER JOIN
                data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
            INNER JOIN
                agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
            WHERE
                data_sources.approval_status = 'approved'
        """

        self.cursor.execute(sql_query, (joined_column_names,))
        results = self.cursor.fetchall()
        # NOTE: Very big tuple, perhaps very long NamedTuple to be implemented later
        return results

    def get_needs_identification_data_sources(self, columns: list[str]) -> list[tuple[Any, ...]]:
        """
        Returns a list of data sources that need identification from the database.

        :param columns: List of column names to use in the SELECT statement.
        :return: A list of tuples, each containing details of a data source.
        """
        joined_column_names = ", ".join(columns)
        sql_query = """
            SELECT
                %s
            FROM
                data_sources
            WHERE
                approval_status = 'needs identification'
        """

        self.cursor.execute(sql_query, (joined_column_names,))
        results = self.cursor.fetchall()
        # NOTE: Very big tuple, perhaps very long NamedTuple to be implemented later
        return results

    def create_new_data_source_query(self, data: dict) -> str:
        """
        Creates a query to add a new data source to the database.

        :param data: A dictionary containing the data source details.
        """
        column_names = ""
        column_values = ""
        for key, value in data.items():
            if key not in RESTRICTED_COLUMNS:
                column_names += f"{key}, "
                if type(value) == str:
                    column_values += f"'{value}', "
                else:
                    column_values += f"{value}, "

        now = datetime.now().strftime("%Y-%m-%d")
        airtable_uid = str(uuid.uuid4())

        column_names += "approval_status, url_status, data_source_created, airtable_uid"
        column_values += f"False, '[\"ok\"]', '{now}', '{airtable_uid}'"

        sql_query = f"INSERT INTO data_sources ({column_names}) VALUES ({column_values}) RETURNING *"

        return sql_query

    def add_new_data_source(self, data: dict) -> None:
        """
        Processes a request to add a new data source.

        :param data: A dictionary containing the updated data source details.
        """
        sql_query = self.create_new_data_source_query(data)
        self.cursor.execute(sql_query)

    def update_data_source(self, data: dict, data_source_id: str) -> None:
        """
        Processes a request to update a data source.

        :param data_source_id: The data source's ID.
        :param data: A dictionary containing the data source details.
        """
        sql_query = self.create_data_source_update_query(data, data_source_id)
        self.cursor.execute(sql_query)

    def create_data_source_update_query(self, data: dict, data_source_id: str) -> str:
        """
        Creates a query to update a data source in the database.

        :param data: A dictionary containing the updated data source details.
        :param data_source_id: The ID of the data source to be updated.
        """
        data_to_update = ""
        for key, value in data.items():
            if key not in RESTRICTED_COLUMNS:
                if type(value) == str:
                    data_to_update += f"{key} = '{value}', "
                else:
                    data_to_update += f"{key} = {value}, "
        data_to_update = data_to_update[:-2]
        sql_query = f"""
        UPDATE data_sources 
        SET {data_to_update}
        WHERE airtable_uid = '{data_source_id}'
        """
        return sql_query

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
        data_sources = self.cursor.fetchall()

        results = [
            self.MapInfo(
                data_source_id=row[0],
                data_source_name=row[1],
                agency_id=row[2],
                agency_name=row[3],
                state=row[4],
                municipality=row[5],
                county=row[6],
                record_type=row[7],
                lat=row[8],
                lng=row[9],
            )
            for row in data_sources
        ]

        return results

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
        # NOTE: Very big tuple, perhaps very long NamedTuple to be implemented later
        return results

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
        (the data source has not been archived previously OR the data source is updated regularly)
        AND the source url is not broken
        AND the source url is not null.

        :return: A list of ArchiveInfo namedtuples, each containing archive details of a data source.
        """
        sql_query = """
        SELECT
            airtable_uid,
            source_url,
            update_frequency,
            last_cached,
            broken_source_url_as_of
        FROM
            data_sources
        WHERE 
            (last_cached IS NULL OR update_frequency IS NOT NULL) AND broken_source_url_as_of IS NULL AND url_status <> 'broken' AND source_url IS NOT NULL
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
        sql_query = """
            UPDATE data_sources 
            SET 
                url_status = 'broken', 
                broken_source_url_as_of = %s, 
                last_cached = %s 
            WHERE airtable_uid = %s
        """
        self.cursor.execute(sql_query, (broken_as_of, last_cached, id))

    def update_last_cached(self, id: str, last_cached: str) -> None:
        """
        Updates the last_cached field in the data_sources table for a given id.

        :param id: The airtable_uid of the data source.
        :param last_cached: The last cached date to be updated.
        """
        sql_query = "UPDATE data_sources SET last_cached = %s WHERE airtable_uid = %s"
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
        sql_query = QUICK_SEARCH_SQL.format(search.title(), location.title())

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

    def add_new_access_token(self) -> None:
        """Inserts a new access token into the database."""
        # NOTE: May refactor next two lines so that the function is sent the
        #       token and expiration instead of generating it here
        token = uuid.uuid4().hex
        expiration = datetime.now() + datetime.timedelta(minutes=5)
        self.cursor.execute(
            f"insert into access_tokens (token, expiration_date) values (%s, %s)",
            (token, expiration),
        )

    UserInfo = namedtuple("UserInfo", ["id", "password_digest", "api_key"])

    def get_user_info(self, email: str) -> UserInfo:
        """
        Retrieves user data by email.

        :param email: User's email.
        :raise UserNotFoundError: If no user is found.
        :return: UserInfo namedtuple containing the user's information.
        """
        self.cursor.execute(
            f"select id, password_digest, api_key from users where email = %s", (email,)
        )
        results = self.cursor.fetchone()
        if len(results) == 0:
            raise UserNotFoundError(email)

        return self.UserInfo(
            id=results[0],
            password_digest=results[1],
            api_key=results[2],
        )

    def add_new_session_token(self, session_token, email: str, expiration) -> None:
        """
        Inserts a session token into the database.

        :param session_token: The session token.
        :param email: User's email.
        :param expiration: The session token's expiration.
        """
        self.cursor.execute(
            f"insert into session_tokens (token, email, expiration_date) values (%s, %s, %s)",
            (session_token, email, expiration),
        )

    SessionTokenUserData = namedtuple("SessionTokenUserData", ["id", "email"])

    def get_user_info_by_session_token(self, token: str) -> SessionTokenUserData:
        """
        Retrieves user info from the database using a session token.

        :param token: The session token.
        :raise TokenNotFoundError: If the session token is not found.
        :return: SessionTokenUserData namedtuple with the user's ID and email.
        """
        self.cursor.execute(
            f"select id, email from session_tokens where token = %s", (token,)
        )
        results = self.cursor.fetchone()
        if len(results) == 0:
            raise TokenNotFoundError("The specified token was not found.")
        return self.SessionTokenUserData(id=results[0], email=results[1])

    def delete_session_token(self, old_token: str) -> None:
        """
        Deletes a session token from the database.

        :param old_token: The session token.
        """
        self.cursor.execute(
            f"delete from session_tokens where token = '%s'", (old_token,)
        )

    AccessToken = namedtuple("AccessToken", ["id", "token"])

    def get_access_token(self, api_key: str) -> AccessToken:
        """
        Retrieves an access token from the database.

        :param api_key: The access token.
        :raise AccessTokenNotFoundError: If the access token is not found.
        :returns: AccessToken namedtuple with the ID and the access token.
        """
        self.cursor.execute(
            f"select id, token from access_tokens where token = %s", (api_key,)
        )
        results = self.cursor.fetchone()
        if not results:
            raise AccessTokenNotFoundError("Access token not found")
        return self.AccessToken(id=results[0], token=results[1])

    def delete_expired_access_tokens(self) -> None:
        """Deletes all expired access tokens from the database."""
        self.cursor.execute(f"delete from access_tokens where expiration_date < NOW()")
