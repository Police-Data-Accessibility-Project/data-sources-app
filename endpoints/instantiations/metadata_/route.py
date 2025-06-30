from flask import Response

from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import API_OR_JWT_AUTH_INFO
from middleware.decorators.endpoint_info import endpoint_info
from middleware.primary_resource_logic.metadata import (
    get_record_types_and_categories,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_metadata = create_namespace(AppNamespaces.METADATA)


@namespace_metadata.route("/record-types-and-categories", methods=["GET"])
class RecordTypeAndCategory(PsycopgResource):
    @endpoint_info(
        namespace=namespace_metadata,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.RECORD_TYPE_AND_CATEGORY_GET,
        response_info=ResponseInfo(
            success_message="Returns a list of record types and categories."
        ),
        description="Get a list of record types and categories",
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_record_types_and_categories,
        )
