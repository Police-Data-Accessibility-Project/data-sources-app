from db.client.core import DatabaseClient
from endpoints.v3.source_manager.follows.query import GetUserFollowsSourceCollectorQueryBuilder


def test_user_follows_source_collector_query_builder(
    live_database_client: DatabaseClient,
):
    live_database_client.run_query_builder(
        GetUserFollowsSourceCollectorQueryBuilder()
    )

