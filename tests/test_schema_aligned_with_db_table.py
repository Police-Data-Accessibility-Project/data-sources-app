"""
Test that a given schema's fields align with the columns of a database relation
"""

from middleware.enums import Relations
from middleware.primary_resource_logic.agencies import (
    AgencyInfoBaseSchema,
    AgenciesGetSchema,
)
from tests.fixtures import live_database_client


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
    agencies_expanded_columns = live_database_client.get_columns_for_relation(
        Relations.AGENCIES_EXPANDED
    )
    schema = AgenciesGetSchema()
    schema_fields = [field for field in schema.fields]

    schema_fields.sort()
    agencies_expanded_columns.sort()

    assert schema_fields == agencies_expanded_columns
