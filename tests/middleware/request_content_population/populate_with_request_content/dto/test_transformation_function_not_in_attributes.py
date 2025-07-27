import pytest

from middleware.schema_and_dto.dynamic.dto_request_content_population import populate_dto_with_request_content
from middleware.schema_and_dto.exceptions import AttributeNotInClassError
from middleware.schema_and_dto.non_dto_dataclasses import DTOPopulateParameters
from tests.middleware.request_content_population.data import SimpleDTO
from utilities.enums import SourceMappingEnum


def test_populate_dto_with_request_transformation_function_not_in_attributes(
    patched_get_data_from_source,
):
    """
    Test that an error is raised if the attribute provided in the transformation function is not in the attributes
    :return:
    """
    with pytest.raises(AttributeNotInClassError):
        populate_dto_with_request_content(
            DTOPopulateParameters(
                dto_class=SimpleDTO,
                transformation_functions={
                    "non_existent_attribute": lambda value: value
                },
                source=SourceMappingEnum.QUERY_ARGS,
            )
        )
