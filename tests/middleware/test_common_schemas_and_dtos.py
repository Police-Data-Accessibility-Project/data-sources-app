import pytest
from marshmallow import ValidationError

from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestSchema,
)


def test_entry_data_request_schema_success():

    schema = EntryDataRequestSchema()
    schema.load({"entry_data": {"entry_name": "test entry", "data": 1}})
    # Should load successfully.


def test_entry_data_request_schema_fail():

    schema = EntryDataRequestSchema()
    # Test on two-level dictionary
    with pytest.raises(ValidationError):
        schema.load({"entry_data": {"data": {"second_level": 1}}})
    # Test on incorrect field
    with pytest.raises(ValidationError):
        schema.load({"data": {"entry_name": 1}})
