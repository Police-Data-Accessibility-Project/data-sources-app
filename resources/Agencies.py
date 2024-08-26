from flask import Response
from flask_restx import fields

from middleware.agencies import get_agencies
from middleware.decorators import api_key_required, permissions_required
from middleware.enums import PermissionsEnum
from resources.resource_helpers import add_api_key_header_arg
from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_agencies = create_namespace()

inner_model = namespace_agencies.model(
    "Agency Item",
    {
        "name": fields.String(required=True, description="The name of the agency"),
        "homepage_url": fields.String(description="The homepage URL of the agency"),
        "count_data_sources": fields.Integer(description="The count of data sources"),
        "agency_type": fields.String(description="The type of the agency"),
        "multi_agency": fields.Boolean(
            description="Indicates if the agency is multi-agency"
        ),
        "submitted_name": fields.String(description="The submitted name of the agency"),
        "jurisdiction_type": fields.String(
            description="The jurisdiction type of the agency"
        ),
        "state_iso": fields.String(description="The ISO code of the state"),
        "municipality": fields.String(description="The municipality of the agency"),
        "zip_code": fields.String(description="The ZIP code of the agency"),
        "county_fips": fields.String(description="The FIPS code of the county"),
        "county_name": fields.String(description="The name of the county"),
        "lat": fields.Float(description="The latitude of the agency location"),
        "lng": fields.Float(description="The longitude of the agency location"),
        "data_sources": fields.String(
            description="The data sources related to the agency"
        ),
        "no_web_presence": fields.Boolean(
            description="Indicates if the agency has no web presence"
        ),
        "airtable_agency_last_modified": fields.DateTime(
            description="The last modified date in Airtable"
        ),
        "data_sources_last_updated": fields.DateTime(
            description="The last updated date of data sources"
        ),
        "approved": fields.Boolean(description="Indicates if the agency is approved"),
        "rejection_reason": fields.String(
            description="The reason for rejection, if any"
        ),
        "last_approval_editor": fields.String(description="The last approval editor"),
        "agency_created": fields.DateTime(
            description="The creation date of the agency"
        ),
        "county_airtable_uid": fields.String(
            description="The Airtable UID of the county"
        ),
        "defunct_year": fields.Integer(
            description="The year the agency became defunct"
        ),
        "airtable_uid": fields.String(description="The Airtable UID of the agency"),
    },
)

output_model = namespace_agencies.model(
    "Agencies Result",
    {
        "count": fields.Integer(description="Total count of agencies"),
        "data": fields.List(fields.Nested(inner_model), description="List of agencies"),
    },
)

parser = namespace_agencies.parser()
parser.add_argument(
    "page",
    type=int,
    required=True,
    location="args",
    help="The page number of results to return.",
    default=1,
)
add_api_key_header_arg(parser)


@namespace_agencies.route("/agencies/<page>")
@namespace_agencies.expect(parser)
@namespace_agencies.doc(
    description="Get a paginated list of approved agencies from the database.",
    responses={
        200: "Success. Returns a paginated list of approved agencies.",
        500: "Internal server error.",
        403: "Unauthorized. Forbidden or an invalid API key.",
        400: "Bad request. Missing or bad API key",
    },
)
class Agencies(PsycopgResource):
    """Represents a resource for fetching approved agency data from the database."""

    @handle_exceptions
    @api_key_required
    @namespace_agencies.response(
        200,
        "Success. Returns a paginated list of approved agencies.",
        model=output_model,
    )
    # @namespace_agencies.marshal_with(output_model)
    def get(self, page: int) -> Response:
        """
        Retrieves a paginated list of approved agencies from the database.

        Returns:
        - dict: A dictionary containing the count of returned agencies and their data.
        """
        return self.run_endpoint(get_agencies, page=int(page))
