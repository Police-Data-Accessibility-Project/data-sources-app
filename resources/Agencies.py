import psycopg2
import psycopg2.extras
from flask import Response

from middleware.agencies import get_agencies
from middleware.security import api_required
from resources.PsycopgResource import PsycopgResource, handle_exceptions

from utilities.common import convert_dates_to_strings
from typing import Dict, Any


approved_columns = [
    "name",
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
    "airtable_uid",
]


class Agencies(PsycopgResource):
    """Represents a resource for fetching approved agency data from the database."""

    @handle_exceptions
    @api_required
    def get(self, page: str) -> Response:
        """
        Retrieves a paginated list of approved agencies from the database.

        Parameters:
        - page (str): The page number of results to return.

        Returns:
        - dict: A dictionary containing the count of returned agencies and their data.
        """
        with self.setup_database_client() as db_client:
            return get_agencies(db_client, int(page))
