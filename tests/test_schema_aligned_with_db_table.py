"""
Test that a given schema's fields align with the columns of a database relation
"""
from marshmallow import Schema

from database_client.database_client import DatabaseClient
from middleware.enums import Relations
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_schemas import AgencyInfoBaseSchema, AgenciesGetSchema
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_schemas import DataRequestsSchema
from tests.conftest import live_database_client


def assert_relation_columns_and_schema_fields_aligned(
    live_database_client: DatabaseClient,
    relation: Relations,
    schema: Schema
):
    schema_fields = [field for field in schema.fields]
    relation_columns = live_database_client.get_columns_for_relation(relation)
    schema_fields.sort()
    relation_columns.sort()
    assert schema_fields == relation_columns

def test_agencies_post_schema_aligned_with_agencies_expanded(live_database_client):
    """
    Test that the fields of AgenciesPostSchema are a subset of the columns of `agencies_expanded`
    :return:
    """
    agencies_expanded_columns = live_database_client.get_columns_for_relation(
        Relations.AGENCIES_EXPANDED
    )
    schema = AgencyInfoBaseSchema()
    for field in schema.fields:
        assert field in agencies_expanded_columns


def test_agencies_get_schema_aligned_with_agencies_expanded(live_database_client):
    """
    Test that the fields of AgenciesGetSchema are equivalent to the columns of `agencies_expanded`
    :return:
    """
    assert_relation_columns_and_schema_fields_aligned(
        live_database_client,
        Relations.AGENCIES_EXPANDED,
        AgenciesGetSchema()
    )


def test_data_request_schema_aligned_with_data_requests_table(live_database_client):
    assert_relation_columns_and_schema_fields_aligned(
        live_database_client,
        Relations.DATA_REQUESTS,
        DataRequestsSchema()
    )
