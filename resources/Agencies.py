from flask import Response
from flask_restx import fields

from middleware.access_logic import AccessInfo
from middleware.agencies import (
    get_agencies,
    get_agency_by_id,
    create_agency,
    update_agency,
    delete_agency,
)
from middleware.column_permission_logic import create_column_permissions_string_table
from middleware.custom_dataclasses import EntryDataRequest
from middleware.decorators import (
    authentication_required,
)
from middleware.enums import AccessTypeEnum, PermissionsEnum, Relations
from resources.resource_helpers import (
    create_entry_data_model,
    add_jwt_or_api_key_header_arg,
    add_jwt_header_arg,
    create_response_dictionary,
    create_id_and_message_model,
)
from utilities.namespace import create_namespace, AppNamespaces
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from utilities.populate_dto_with_request_content import (
    DTOPopulateParameters,
    SourceMappingEnum,
)

namespace_agencies = create_namespace(
    AppNamespaces.AGENCIES,
)

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

agencies_entry_model = create_entry_data_model(namespace_agencies)

page_parser = namespace_agencies.parser()
page_parser.add_argument(
    "page",
    type=int,
    required=True,
    location="path",
    help="The page number of results to return.",
    default=1,
)
add_jwt_or_api_key_header_arg(page_parser)

post_parser = namespace_agencies.parser()
add_jwt_header_arg(post_parser)

id_parser_get = namespace_agencies.parser()
add_jwt_or_api_key_header_arg(id_parser_get)

id_parser_admin = namespace_agencies.parser()
add_jwt_header_arg(id_parser_admin)

id_and_message_model = create_id_and_message_model(namespace_agencies)

agencies_column_permissions = create_column_permissions_string_table(
    relation=Relations.AGENCIES.value
)


@namespace_agencies.route("/")
class AgenciesPost(PsycopgResource):

    @handle_exceptions
    @namespace_agencies.doc(
        description=f"""
        Adds a new agency.
        
Columns permitted to be included by the user is determined by their level of access

## COLUMN PERMISSIONS

{agencies_column_permissions}
        """,
        responses=create_response_dictionary(
            success_message="Returns the id of the newly created agency.",
            success_model=id_and_message_model,
        ),
    )
    @namespace_agencies.expect(agencies_entry_model, post_parser)
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
        restrict_to_permissions=[PermissionsEnum.DB_WRITE],
    )
    def post(self, access_info: AccessInfo):
        return self.run_endpoint(
            wrapper_function=create_agency,
            dto_populate_parameters=DTOPopulateParameters(
                dto_class=EntryDataRequest, source=SourceMappingEnum.JSON
            ),
            access_info=access_info,
        )
        pass


@namespace_agencies.route("/page/<page>")
@namespace_agencies.expect(page_parser)
class AgenciesByPage(PsycopgResource):
    """Represents a resource for fetching approved agency data from the database."""

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT, AccessTypeEnum.API_KEY],
    )
    @namespace_agencies.doc(
        description=f"""
Get a paginated list of approved agencies from the database.

Columns returned are determined by the user's access level.

## COLUMN PERMISSIONS

{agencies_column_permissions}
""",
        responses=create_response_dictionary(
            success_message="Returns a paginated list of approved agencies.",
            success_model=output_model,
        ),
    )
    def get(self, page: int, access_info: AccessInfo) -> Response:
        """
        Retrieves a paginated list of approved agencies from the database.

        Returns:
        - dict: A dictionary containing the count of returned agencies and their data.
        """
        return self.run_endpoint(get_agencies, access_info=access_info, page=int(page))


@namespace_agencies.route("/id/<agency_id>")
class AgenciesById(PsycopgResource):

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT, AccessTypeEnum.API_KEY],
    )
    @namespace_agencies.expect(id_parser_get)
    @namespace_agencies.doc(
        description=f"""
        Get Agency by id

Columns returned are determined by the user's access level.

## COLUMN PERMISSIONS

{agencies_column_permissions}
        """,
        responses=create_response_dictionary("Returns agency.", inner_model),
    )
    def get(self, agency_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            get_agency_by_id, access_info=access_info, agency_id=agency_id
        )

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
        restrict_to_permissions=[PermissionsEnum.DB_WRITE],
    )
    @namespace_agencies.expect(id_parser_admin, agencies_entry_model)
    @namespace_agencies.doc(
        description=f"""
        Updates Agency
        
Columns allowed to be updated by the user is determined by their level of access

## COLUMN PERMISSIONS

{agencies_column_permissions}

""",
        responses=create_response_dictionary("Agency successfully updated."),
    )
    def put(self, agency_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            update_agency,
            dto_populate_parameters=DTOPopulateParameters(
                dto_class=EntryDataRequest, source=SourceMappingEnum.JSON
            ),
            access_info=access_info,
            agency_id=agency_id,
        )

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
        restrict_to_permissions=[PermissionsEnum.DB_WRITE],
    )
    @namespace_agencies.expect(id_parser_admin)
    @namespace_agencies.doc(
        description="Deletes Agency",
        responses=create_response_dictionary("Agency successfully deleted."),
    )
    def delete(self, agency_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            delete_agency, agency_id=agency_id, access_info=access_info
        )
