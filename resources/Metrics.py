from flask import Response

from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import API_OR_JWT_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.metrics_logic import get_metrics
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import AppNamespaces, create_namespace

namespace_metrics = create_namespace(AppNamespaces.METRICS)


@namespace_metrics.route("")
class Metrics(PsycopgResource):

    @endpoint_info(
        namespace=namespace_metrics,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.METRICS_GET,
        description="Returns the metrics for the application.",
        response_info=ResponseInfo(
            success_message="Returns the metrics for the application."
        ),
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_metrics,
        )
