from flask import make_response

from db.client import DatabaseClient
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto.dtos.metrics import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)


def get_metrics(db_client: DatabaseClient):
    return db_client.get_metrics()


def get_metrics_followed_searches_breakdown(
    db_client: DatabaseClient, dto: MetricsFollowedSearchesBreakdownRequestDTO
):
    return make_response(
        {"results": db_client.get_metrics_followed_searches_breakdown(dto=dto)}
    )


def get_metrics_followed_searches_aggregate(db_client: DatabaseClient):
    result = db_client.get_metrics_followed_searches_aggregate()
    return result
