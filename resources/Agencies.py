from flask_restful import Resource
from flask import request, jsonify
from middleware.security import api_required
from utilities.common import convert_dates_to_strings
import json

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


class Agencies(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def get(self, page):
        try:
            cursor = self.psycopg2_connection.cursor()
            joined_column_names = ", ".join(approved_columns)
            offset = (int(page) - 1) * 1000
            cursor.execute(
                f"select {joined_column_names} from agencies where approved = 'TRUE' limit 1000 offset {offset}"
            )
            results = cursor.fetchall()
            agencies_matches = [
                dict(zip(approved_columns, result)) for result in results
            ]

            for item in agencies_matches:
                convert_dates_to_strings(item)

            agencies = {"count": len(agencies_matches), "data": agencies_matches}

            return agencies

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return "There has been an error pulling data!"
