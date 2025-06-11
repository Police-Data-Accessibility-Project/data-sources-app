from flask import Response

from endpoints.schema_config.instantiations.metrics.followed_searches.breakdown import (
    MetricsFollowedSearchesBreakdownGetEndpointSchemaConfig,
)
from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import API_OR_JWT_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.metrics import (
    get_metrics,
    get_metrics_followed_searches_breakdown,
    get_metrics_followed_searches_aggregate,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
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


@namespace_metrics.route("/followed-searches/breakdown")
class MetricsFollowedSearchesBreakdown(PsycopgResource):

    @endpoint_info(
        namespace=namespace_metrics,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.METRICS_FOLLOWED_SEARCHES_BREAKDOWN_GET,
        description="Returns the metrics for followed searches, broken down by followed search.",
        response_info=ResponseInfo(
            success_message="Returns the metrics for followed searches."
        ),
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_metrics_followed_searches_breakdown,
            schema_populate_parameters=MetricsFollowedSearchesBreakdownGetEndpointSchemaConfig.get_schema_populate_parameters(),
        )


@namespace_metrics.route("/followed-searches/aggregate")
class MetricsFollowedSearchesAggregate(PsycopgResource):

    @endpoint_info(
        namespace=namespace_metrics,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.METRICS_FOLLOWED_SEARCHES_AGGREGATE_GET,
        description="Returns the aggregated metrics for followed searches",
        response_info=ResponseInfo(
            success_message="Returns the aggregated metrics for followed searches."
        ),
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_metrics_followed_searches_aggregate,
        )
