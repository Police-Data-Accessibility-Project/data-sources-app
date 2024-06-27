from collections import namedtuple
from typing import Union, Optional

import psycopg2


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
        return self.ResetTokenInfo(
            id=row[0], email=row[1], create_date=row[2]
        )

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
        return self.SessionTokenInfo(
            email=row[0], expiration_date=row[1]
        )

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
        return self.RoleInfo(
            id=row[0], role=row[1]
        )

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
    

    DATA_SOURCES_APPROVED_COLUMNS = [
        "name",
        "submitted_name",
        "description",
        "record_type",
        "source_url",
        "agency_supplied",
        "supplying_entity",
        "agency_originated",
        "originating_entity",
        "agency_aggregation",
        "coverage_start",
        "coverage_end",
        "source_last_updated",
        "retention_schedule",
        "detail_level",
        "number_of_records_available",
        "size",
        "access_type",
        "data_portal_type",
        "record_format",
        "update_frequency",
        "update_method",
        "tags",
        "readme_url",
        "scraper_url",
        "data_source_created",
        "airtable_source_last_modified",
        "url_status",
        "rejection_note",
        "last_approval_editor",
        "agency_described_submitted",
        "agency_described_not_in_database",
        "approval_status",
        "record_type_other",
        "data_portal_type_other",
        "records_not_online",
        "data_source_request",
        "url_button",
        "tags_other",
        "access_notes",
        "last_cached",
    ]

    AGENCY_APPROVED_COLUMNS = [
        "homepage_url",
        "count_data_sources",
        "agency_type",
        "multi_agency",
        "submitted_name",
        "jurisdiction_type",
        "state_iso",
        "municipality",
        "zip_code",
        "county_fips",
        "county_name",
        "lat",
        "lng",
        "data_sources",
        "no_web_presence",
        "airtable_agency_last_modified",
        "data_sources_last_updated",
        "approved",
        "rejection_reason",
        "last_approval_editor",
        "agency_created",
        "county_airtable_uid",
        "defunct_year",
    ]


    def get_data_source_by_id(self, data_source_id: str) -> tuple[Any, ...]:
        """
        Get a data source by its ID, including related agency information.

        :param data_source_id: The unique identifier for the data source.
        :return: A dictionary containing the data source and its related agency details. None if not found.
        """
        data_source_approved_columns = [
            f"data_sources.{approved_column}"
            for approved_column in DATA_SOURCES_APPROVED_COLUMNS
        ]
        agencies_approved_columns = [
            f"agencies.{field}" for field in AGENCY_APPROVED_COLUMNS
        ]
        all_approved_columns = data_source_approved_columns + agencies_approved_columns
        all_approved_columns.append("data_sources.airtable_uid as data_source_id")
        all_approved_columns.append("agencies.airtable_uid as agency_id")
        all_approved_columns.append("agencies.name as agency_name")

        joined_column_names = ", ".join(all_approved_columns)
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

        self.cursor.execute(sql_query, (joined_column_names, data_source_id,))
        result = self.cursor.fetchone()
        # NOTE: Very big tuple, perhaps very long NamedTuple to be implemented later
        return result


    def get_approved_data_sources(self) -> list[tuple[Any, ...]]:
        """
        Fetches all approved data sources and their related agency information.

        :return: A list of tuples, each containing details of a data source and its related agency.
        """
        data_source_approved_columns = [
            f"data_sources.{approved_column}"
            for approved_column in DATA_SOURCES_APPROVED_COLUMNS
        ]
        data_source_approved_columns.append("agencies.name as agency_name")

        joined_column_names = ", ".join(data_source_approved_columns)

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

        self.cursor.execute(sql_query, (joined_column_names))
        results = self.cursor.fetchall()
        # NOTE: Very big tuple, perhaps very long NamedTuple to be implemented later
        return results

    
    def get_needs_identification_data_sources(self) -> list[tuple[Any, ...]]:
        """
        Returns a list of data sources that need identification.

        :return: A list of tuples, each containing details of a data source.
        """
        joined_column_names = ", ".join(DATA_SOURCES_APPROVED_COLUMNS)

        sql_query = """
            SELECT
                %s
            FROM
                data_sources
            WHERE
                approval_status = 'needs identification'
        """

        self.cursor.execute(sql_query, (joined_column_names))
        results = self.cursor.fetchall()

        return results
