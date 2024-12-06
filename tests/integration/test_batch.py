import os
from dataclasses import dataclass
from enum import Enum
from typing import TextIO, Optional, Annotated

import pytest

from marshmallow import Schema
from csv import DictWriter
import tempfile

from conftest import test_data_creator_flask, monkeysession
from database_client.enums import LocationType
from middleware.schema_and_dto_logic.primary_resource_schemas.batch_schemas import (
    AgenciesPostRequestFlatBaseSchema,
    DataSourcesPostRequestFlatBaseSchema,
    AgenciesPutRequestFlatBaseSchema,
    DataSourcesPutRequestFlatBaseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_base_schema import (
    DataRequestsSchema,
)
from resources.endpoint_schema_config import EndpointSchemaConfig, SchemaConfigs
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.helper_classes.MultipleTemporaryFiles import (
    MultipleTemporaryFiles,
)
from tests.helper_scripts.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


SUFFIX_ARRAY = [".csv", ".csv", ".inv", ".csv"]


# Helper scripts
#
class ResourceType(Enum):
    AGENCY = "agencies"
    SOURCE = "data_sources"
    REQUEST = "data_requests"


def get_endpoint_nomenclature(
    resource_type: ResourceType,
) -> str:
    """
    Get a string version of the resource, appropriate for endpoints.
    """
    return resource_type.value.replace("_", "-")


@dataclass
class TestFiles:
    file_no_errors: TextIO
    file_with_errors: TextIO
    file_incorrect_type: TextIO
    file_duplicates: TextIO


@dataclass
class TestRunner:
    resource_type: ResourceType
    test_data_creator: TestDataCreatorFlask
    test_files: TestFiles


class TestCSVCreator:

    def __init__(self, schema: Schema):
        self.fields = schema.fields

    def create_csv(self, file: TextIO, rows: list[dict]):
        header = list(self.fields.keys())
        writer = DictWriter(file, fieldnames=header)
        # Write header row using header
        writer.writerow({field: field for field in header})

        for row in rows:
            writer.writerow(row)
        file.close()


@dataclass
class BatchTestRunner:
    tdc: TestDataCreatorFlask
    csv_creator: TestCSVCreator
    schema: Optional[Annotated[Schema, "The schema to use in the test"]] = None

    def generate_test_data(self, override: Optional[dict] = None):
        return generate_test_data_from_schema(
            schema=self.schema,
            override=override
        )


@pytest.fixture
def runner(
    test_data_creator_flask: TestDataCreatorFlask,
):
    return BatchTestRunner(
        tdc=test_data_creator_flask,
        csv_creator=TestCSVCreator(AgenciesPostRequestFlatBaseSchema()),
    )


@pytest.fixture
def agencies_post_runner(runner: BatchTestRunner):
    runner.schema = AgenciesPostRequestFlatBaseSchema()
    return runner


@pytest.fixture
def sources_post_runner(runner: BatchTestRunner):
    runner.schema = DataSourcesPostRequestFlatBaseSchema()
    return runner


@pytest.fixture
def agencies_put_runner(runner: BatchTestRunner):
    runner.schema = AgenciesPutRequestFlatBaseSchema()
    return runner


@pytest.fixture
def sources_put_runner(runner: BatchTestRunner):
    runner.schema = DataSourcesPutRequestFlatBaseSchema()
    return runner


def run_insert_test(runner: TestRunner):
    endpoint_nomenclature = get_endpoint_nomenclature(runner.resource_type)
    batch_endpoint = f"/batch/{endpoint_nomenclature}"
    tf = runner.test_files

    def run_endpoint(file: TextIO):
        return run_and_validate_request(
            endpoint=batch_endpoint,
            http_method="post",
            flask_client=runner.test_data_creator.flask_client,
            file=file,
        ).json

    # File 1 should occur without error
    # For all ids returned, confirm their presence
    data = run_endpoint(tf.file_no_errors)

    # File 2 should contain two errors and one correct value
    # For all ids returned without error, confirm their presence.
    data = run_endpoint(tf.file_with_errors)

    # File 3 should be of an incorrect file type
    data = run_endpoint(tf.file_incorrect_type)

    # File 4 should contain two rows which are duplicates with each other
    # These rows should be rejected by all others accepted
    data = run_endpoint(tf.file_duplicates)

    pytest.fail("Not implemented")


#
# def run_update_test(
#     runner: TestRunner
# ):
#
#     # File 1 should occur without error
#     # For all ids returned, confirm the attributes are correct
#         # via GET-BY-ID request to relevant endpoint
#
#     # File 2 should contain two errors and one correct value
#     # For all ids returned without error, confirm their attributes are correct.
#
#     # File 3 should be of an incorrect file type
#
#     # File 4 should contain two rows which are duplicates with each other.
#     # These rows should be rejected but all others accepted
#     pytest.fail("Not implemented")

class SimpleTempFile:

    def __init__(self, suffix: str = ".csv"):
        self.suffix = suffix
        self.temp_file = None

    def __enter__(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w+",
            encoding="utf-8",
            suffix=self.suffix,
            delete=False
        )
        return self.temp_file

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.temp_file.close()
            os.unlink(self.temp_file.name)
        except Exception as e:
            print(f"Error cleaning up temporary file {self.temp_file.name}: {e}")






def test_batch_requests_insert(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    schema = SchemaConfigs.DATA_REQUESTS_POST.value.input_schema
    csv_creator = TestCSVCreator(schema=schema)

    def generate_test_data(override: Optional[dict] = None):
        request_info = generate_test_data_from_schema(
            schema=DataRequestsSchema(
                only=[
                    "title",
                    "submission_notes",
                    "data_requirements",
                    "request_urgency",
                    "coverage_range",
                ]
            ),
            override=override,
        )
        location_infos = [
            {
                "state": "Pennsylvania",
                "county": "Allegheny",
                "locality": "Pittsburgh",
                "type": LocationType.LOCALITY.value,
            }
        ]
        return {"request_info": request_info, "location_infos": location_infos}

    with MultipleTemporaryFiles(suffixes=SUFFIX_ARRAY) as temp_files:
        test_files = TestFiles(
            file_no_errors=temp_files[0],
            file_with_errors=temp_files[1],
            file_incorrect_type=temp_files[2],
            file_duplicates=temp_files[3],
        )
        csv_creator.create_csv(
            file=test_files.file_no_errors,
            rows=[generate_test_data(), generate_test_data(), generate_test_data()],
        )
        csv_creator.create_csv(
            file=test_files.file_with_errors,
            rows=[
                generate_test_data(override={"title": None}),
                generate_test_data(),
                generate_test_data(override={"request_urgency": "gibberish"}),
            ],
        )
        dict_to_duplicate = generate_test_data()
        csv_creator.create_csv(
            file=test_files.file_duplicates,
            rows=[dict_to_duplicate, generate_test_data(), dict_to_duplicate],
        )

        runner = TestRunner(
            resource_type=ResourceType.REQUEST,
            test_data_creator=tdc,
            test_files=test_files,
        )

        run_insert_test(runner=runner)

    # pytest.fail("Not implemented")


#
# def test_batch_requests_update(
#     test_data_creator_flask: TestDataCreatorFlask,
# ):
#     pytest.fail("Not implemented")


def generate_agencies_locality_data():
    locality_name = get_test_name()
    return {
        "location_type": LocationType.LOCALITY.value,
        "locality_name": locality_name,
        "county_fips": "42003",
        "state_iso": "PA",
    }


def test_batch_agencies_insert_happy_path(
    agencies_post_runner: BatchTestRunner,
):
    runner = agencies_post_runner

    locality_info = generate_agencies_locality_data()
    rows = [runner.generate_test_data(override=locality_info) for _ in range(3)]
    with SimpleTempFile() as temp_file:
        runner.csv_creator.create_csv(
            file=temp_file,
            rows=rows
        )
        data = runner.tdc.request_validator.insert_agencies_batch(
            file=temp_file,
            headers=runner.tdc.get_admin_tus().jwt_authorization_header
        )

    ids = data["ids"]

    for row, id in zip(rows, ids):
        data = runner.tdc.request_validator.get_agency_by_id(
            id=id,
            headers=runner.tdc.get_admin_tus()
        )
        assert row.items() <= data.items()


def test_batch_agencies_insert(
    test_data_creator_flask: TestDataCreatorFlask,
):
    schema = AgenciesPostRequestFlatBaseSchema()
    csv_creator = TestCSVCreator(schema=schema)

    def generate_test_data(override: Optional[dict] = None):
        return generate_test_data_from_schema(schema=schema)

    data = generate_test_data()

    with MultipleTemporaryFiles(suffixes=SUFFIX_ARRAY) as temp_files:
        test_files = TestFiles(
            file_no_errors=temp_files[0],
            file_with_errors=temp_files[1],
            file_incorrect_type=temp_files[2],
            file_duplicates=temp_files[3],
        )
        csv_creator.create_csv(
            file=test_files.file_no_errors,
            rows=[
                generate_test_data(),
                generate_test_data(),
                generate_test_data(),
            ],
        )

    pytest.fail("Not implemented")


def test_batch_agencies_update(
    test_data_creator_flask: TestDataCreatorFlask,
):
    pytest.fail("Not implemented")


def test_batch_sources_insert(
    test_data_creator_flask: TestDataCreatorFlask,
):
    pytest.fail("Not implemented")


def test_batch_sources_update(
    test_data_creator_flask: TestDataCreatorFlask,
):
    pytest.fail("Not implemented")
