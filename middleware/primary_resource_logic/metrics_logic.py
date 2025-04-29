from database_client.database_client import DatabaseClient
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.primary_resource_dtos.metrics_dtos import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)


def get_metrics(db_client: DatabaseClient):
    return db_client.get_metrics()


def get_metrics_followed_searches_breakdown(
    db_client: DatabaseClient, dto: MetricsFollowedSearchesBreakdownRequestDTO
):
    return FlaskResponseManager.make_response(
        data={"results": db_client.get_metrics_followed_searches_breakdown(dto=dto)}
    )


def get_metrics_followed_searches_aggregate(db_client: DatabaseClient):
    return db_client.get_metrics_followed_searches_aggregate()
