"""
Test that a given schema's fields align with the columns of a database relation
"""

from marshmallow import Schema

from db.client import DatabaseClient
from middleware.enums import Relations
from middleware.schema_and_dto_logic.schemas.data_requests.base import (
    DataRequestsSchema,
)
from tests.conftest import live_database_client


def assert_relation_columns_and_schema_fields_aligned(
    live_database_client: DatabaseClient, relation: Relations, schema: Schema
):
    schema_fields = [field for field in schema.fields]
    relation_columns = live_database_client.get_columns_for_relation(relation)
    schema_fields.sort()
    relation_columns.sort()
    assert schema_fields == relation_columns


def test_data_request_schema_aligned_with_data_requests_table(live_database_client):
    data_request_columns = live_database_client.get_columns_for_relation(
        Relations.DATA_REQUESTS_EXPANDED
    )
    schema = DataRequestsSchema()
    for field in schema.fields:
        assert field in data_request_columns
