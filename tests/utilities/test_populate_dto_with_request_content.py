from dataclasses import dataclass
from typing import Optional
from unittest.mock import MagicMock

import pytest

from tests.helper_scripts.common_mocks_and_patches import patch_request_args_get
from utilities.populate_dto_with_request_content import (
    populate_dto_with_request_content,
    SourceMappingEnum,
    AttributeNotInClassError,
    MutuallyExclusiveArgumentError,
    MissingRequiredArgumentError,
)


@dataclass
class SimpleDTO:
    simple_string: str
    optional_int: Optional[int] = None
    transformed_array: Optional[list[str]] = None


def transform_array(value: str) -> Optional[list[str]]:
    if value is None:
        return None
    return value.split(",")


SAMPLE_REQUEST_ARGS = {
    "simple_string": "spam",
    "optional_int": None,
    "transformed_array": "hello,world",
}

ROUTE_TO_PATCH = "utilities.populate_dto_with_request_content"


@pytest.fixture
def patched_request_args_get(monkeypatch):
    return patch_request_args_get(monkeypatch, ROUTE_TO_PATCH, SAMPLE_REQUEST_ARGS)


@pytest.mark.parametrize(
    "source_mapping_enum",
    (
        SourceMappingEnum.ARGS,
        SourceMappingEnum.FORM,
        SourceMappingEnum.JSON,
    ),
)
def test_populate_dto_with_request_content_happy_path(
    source_mapping_enum, patched_request_args_get
):

    dto = populate_dto_with_request_content(
        SimpleDTO,
        transformation_functions={"transformed_array": transform_array},
        source=source_mapping_enum,
    )
    assert dto.simple_string == "spam"
    assert dto.optional_int is None
    assert dto.transformed_array == ["hello", "world"]


def test_populate_dto_with_request_transformation_function_not_in_attributes(
    patched_request_args_get,
):
    """
    Test that an error is raised if the attribute provided in the transformation function is not in the attributes
    :return:
    """
    with pytest.raises(AttributeNotInClassError):
        dto = populate_dto_with_request_content(
            SimpleDTO,
            transformation_functions={"non_existent_attribute": lambda value: value},
            source=SourceMappingEnum.ARGS,
        )


def test_populate_dto_with_request_no_transformation_functions(
    patched_request_args_get,
):
    dto = populate_dto_with_request_content(
        SimpleDTO,
        source=SourceMappingEnum.ARGS,
    )
    assert dto.simple_string == "spam"
    assert dto.optional_int is None
    assert dto.transformed_array == "hello,world"


def test_populate_dto_with_request_source_mapping_and_source_arguments(
    patched_request_args_get,
):
    with pytest.raises(MutuallyExclusiveArgumentError):
        dto = populate_dto_with_request_content(
            SimpleDTO,
            source=SourceMappingEnum.ARGS,
            attribute_source_mapping={"simple_string": SourceMappingEnum.FORM},
        )


def test_populate_dto_with_request_no_source_argument(
    patched_request_args_get,
):
    with pytest.raises(MissingRequiredArgumentError):
        dto = populate_dto_with_request_content(SimpleDTO)


def test_populate_dto_with_request_source_mapping_happy_path(
    patched_request_args_get,
):
    mock_request = patched_request_args_get
    mock_request.args.get = MagicMock(return_value=1)
    mock_request.form.get = MagicMock(return_value=2)
    mock_request.json.get = MagicMock(return_value=3)
    dto = populate_dto_with_request_content(
        SimpleDTO,
        attribute_source_mapping={
            "simple_string": SourceMappingEnum.ARGS,
            "optional_int": SourceMappingEnum.FORM,
            "transformed_array": SourceMappingEnum.JSON,
        },
    )
    mock_request.json.get.assert_called_once_with("transformed_array")
    mock_request.form.get.assert_called_once_with("optional_int")
    mock_request.args.get.assert_called_once_with("simple_string")

    assert dto.simple_string == 1
    assert dto.optional_int == 2
    assert dto.transformed_array == 3
