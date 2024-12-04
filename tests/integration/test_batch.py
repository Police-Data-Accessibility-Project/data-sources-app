from dataclasses import dataclass
from enum import Enum
from typing import TextIO, Optional

import pytest

from pathlib import Path

from marshmallow import Schema
from pydantic import BaseModel
from csv import DictWriter
import tempfile

from conftest import test_data_creator_flask, monkeysession
from database_client.enums import LocationType
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_base_schema import (
    DataRequestsSchema,
)
from resources.endpoint_schema_config import EndpointSchemaConfig, SchemaConfigs
from tests.helper_scripts.helper_classes.MultipleTemporaryFiles import (
    MultipleTemporaryFiles,
)
from tests.helper_scripts.helper_classes.SchemaTestDataGenerator import (
    SchemaTestDataGenerator,
    generate_test_data_from_schema,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


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
        writer = DictWriter(file, fieldnames=self.fields.keys())
        for row in rows:
            writer.writerow(row)


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
#
#


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
            )
        )
        if override is not None:
            request_info.update(override)
        location_infos = [
            {
                "state": "Pennsylvania",
                "county": "Allegheny",
                "locality": "Pittsburgh",
                "type": LocationType.LOCALITY.value,
            }
        ]
        return {"request_info": request_info, "location_infos": location_infos}

    with MultipleTemporaryFiles(
        suffixes=[".csv", ".csv", ".inv", ".csv"]
    ) as temp_files:
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
        for file in temp_files:
            file.close()

        runner = TestRunner(
            resource_type=ResourceType.REQUEST,
            test_data_creator=tdc,
            test_files=test_files,
        )

        run_insert_test(runner=runner)

    # pytest.fail("Not implemented")


def test_batch_requests_update(
    test_data_creator_flask: TestDataCreatorFlask,
):
    pytest.fail("Not implemented")


def test_batch_agencies_insert(
    test_data_creator_flask: TestDataCreatorFlask,
):
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
