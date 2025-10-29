from flask import Response, make_response

from db.client.core import DatabaseClient
from endpoints.instantiations.data_sources_.post.request_.model import (
    PostDataSourceOuterRequest,
)
from endpoints.instantiations.data_sources_.post.request_.query import (
    PostDataSourceQuery,
)


def post_data_source_wrapper(
    db_client: DatabaseClient,
    dto: PostDataSourceOuterRequest,
) -> Response:
    ds_id: int = db_client.run_query_builder(PostDataSourceQuery(dto))
    return make_response(
        {
            "message": "Successfully created data source",
            "id": str(ds_id),
        }
    )
