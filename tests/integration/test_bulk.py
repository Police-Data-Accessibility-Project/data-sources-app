from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional, Annotated, Callable

import pytest

from marshmallow import Schema

from conftest import test_data_creator_flask, monkeysession
from database_client.enums import LocationType
from middleware.enums import AgencyType
from middleware.primary_resource_logic.bulk_logic import listify_strings
from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_csv_to_schema_conversion_logic import (
    SchemaUnflattener,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.bulk_schemas import (
    AgenciesPostRequestFlatBaseSchema,
    DataSourcesPostRequestFlatBaseSchema,
    AgenciesPostRequestFlatSchema,
)
from middleware.util import stringify_lists
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.common_asserts import assert_contains_key_value_pairs
from tests.helper_scripts.helper_classes.RequestValidator import RequestValidator
from tests.helper_scripts.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helper_scripts.helper_classes.SimpleTempFile import SimpleTempFile
from tests.helper_scripts.helper_classes.TestCSVCreator import TestCSVCreator
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


@dataclass
class BatchTestRunner:
    tdc: TestDataCreatorFlask
    csv_creator: TestCSVCreator
    schema: Optional[Annotated[Schema, "The schema to use in the test"]] = None

    def generate_test_data(self, override: Optional[dict] = None):
        test_data = generate_test_data_from_schema(
            schema=self.schema, override=override
        )
        stringify_lists(d=test_data)
        return test_data


@pytest.fixture
def runner(
    test_data_creator_flask: TestDataCreatorFlask,
):
    return BatchTestRunner(
        tdc=test_data_creator_flask,
        csv_creator=TestCSVCreator(AgenciesPostRequestFlatBaseSchema()),
    )


@pytest.fixture
def agencies_post_runner(
    test_data_creator_flask: TestDataCreatorFlask,
):
    return BatchTestRunner(
        tdc=test_data_creator_flask,
        csv_creator=TestCSVCreator(AgenciesPostRequestFlatSchema()),
        schema=AgenciesPostRequestFlatSchema(),
    )


@pytest.fixture
def data_sources_post_runner(test_data_creator_flask: TestDataCreatorFlask):
    return BatchTestRunner(
        tdc=test_data_creator_flask,
        csv_creator=TestCSVCreator(DataSourcesPostRequestFlatBaseSchema()),
        schema=DataSourcesPostRequestFlatBaseSchema(),
    )


def generate_agencies_locality_data():
    locality_name = get_test_name()
    return {
        "location_id": "1",
    }


def create_csv_and_run(
    runner: BatchTestRunner,
    rows: list[dict],
    request_validator_method: Callable,
    suffix: str = ".csv",
    expected_response_status: HTTPStatus = HTTPStatus.OK,
    expected_schema: Optional[Schema] = None,
):
    if expected_schema is not None:
        kwargs = {
            "expected_schema": expected_schema,
        }
    else:
        kwargs = {}

    with SimpleTempFile(suffix=suffix) as temp_file:
        runner.csv_creator.create_csv(file=temp_file, rows=rows)
        return request_validator_method(
            bop=RequestValidator.BulkOperationParams(
                file=temp_file,
                headers=runner.tdc.get_admin_tus().jwt_authorization_header,
                expected_response_status=expected_response_status,
            ),
            **kwargs,
        )


def check_for_errors(data: dict, check_ids: bool = True):
    if check_ids:
        ids = data["ids"]
        assert len(ids) == 1
    assert len(data["errors"]) == 2, f"Incorrect number of errors: {data['errors']}"
    assert "0", "2" in data["errors"].keys()


def test_batch_agencies_insert_happy_path(
    agencies_post_runner: BatchTestRunner,
):
    runner = agencies_post_runner

    test_name = get_test_name()
    locality_info = {"location_id": runner.tdc.locality(locality_name=test_name)}

    rows = [runner.generate_test_data(override=locality_info) for _ in range(3)]
    data = create_csv_and_run(
        runner=runner,
        rows=rows,
        request_validator_method=runner.tdc.request_validator.insert_agencies_bulk,
    )

    ids = data["ids"]

    unflattener = SchemaUnflattener(flat_schema_class=AgenciesPostRequestFlatBaseSchema)

    for row, id in zip(rows, ids):
        unflattened_row = unflattener.unflatten(flat_data=row)
        data = runner.tdc.request_validator.get_agency_by_id(
            id=id, headers=runner.tdc.get_admin_tus().jwt_authorization_header
        )
        assert_contains_key_value_pairs(
            dict_to_check=data["data"], key_value_pairs=unflattened_row["agency_info"]
        )
        assert data["data"]["locations"][0]["locality_name"] == test_name


def test_batch_agencies_insert_some_errors(
    agencies_post_runner: BatchTestRunner,
):
    runner = agencies_post_runner

    rows = [
        runner.generate_test_data(override={"lat": "not a number"}),
        runner.generate_test_data(override=generate_agencies_locality_data()),
        runner.generate_test_data(override={"lng": "not a number"}),
    ]
    data = create_csv_and_run(
        runner=runner,
        rows=rows,
        request_validator_method=runner.tdc.request_validator.insert_agencies_bulk,
    )

    check_for_errors(data)


def test_batch_agencies_insert_wrong_file_type(
    agencies_post_runner: BatchTestRunner,
):
    runner = agencies_post_runner
    create_csv_and_run(
        runner=agencies_post_runner,
        rows=[],
        suffix=".json",
        request_validator_method=runner.tdc.request_validator.insert_agencies_bulk,
        expected_response_status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        expected_schema=MessageSchema(),
    )


def test_batch_data_sources_insert_happy_path(
    data_sources_post_runner: BatchTestRunner,
):
    runner = data_sources_post_runner
    for _ in range(3):
        runner.tdc.agency()
    rows = [
        runner.generate_test_data(override={"linked_agency_ids": [1, 2, 3]})
        for _ in range(3)
    ]
    data = create_csv_and_run(
        runner=runner,
        rows=rows,
        request_validator_method=runner.tdc.request_validator.insert_data_sources_bulk,
    )
    ids = data["ids"]
    unflattener = SchemaUnflattener(
        flat_schema_class=DataSourcesPostRequestFlatBaseSchema
    )

    for row, id in zip(rows, ids):
        unflattened_row = unflattener.unflatten(flat_data=row)
        data = runner.tdc.request_validator.get_data_source_by_id(
            id=id, headers=runner.tdc.get_admin_tus().jwt_authorization_header
        )
        listify_strings([unflattened_row["entry_data"]])
        assert_contains_key_value_pairs(
            dict_to_check=data["data"],
            key_value_pairs=unflattened_row["entry_data"],
        )


def test_batch_data_sources_insert_some_errors(
    data_sources_post_runner: BatchTestRunner,
):
    runner = data_sources_post_runner
    rows = [
        runner.generate_test_data(override={"linked_agency_ids": "not a list"}),
        runner.generate_test_data(override={"linked_agency_ids": [1, 2, 3]}),
        runner.generate_test_data(override={"coverage_start": "not a date"}),
    ]
    data = create_csv_and_run(
        runner=runner,
        rows=rows,
        request_validator_method=runner.tdc.request_validator.insert_data_sources_bulk,
    )
    check_for_errors(data)


def test_batch_data_sources_insert_wrong_file_type(
    data_sources_post_runner: BatchTestRunner,
):
    runner = data_sources_post_runner
    create_csv_and_run(
        runner=data_sources_post_runner,
        rows=[],
        suffix=".json",
        request_validator_method=runner.tdc.request_validator.insert_data_sources_bulk,
        expected_response_status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        expected_schema=MessageSchema(),
    )
