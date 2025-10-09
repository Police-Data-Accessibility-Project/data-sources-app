from typing import Union

from marshmallow import fields

from middleware.enums import JurisdictionType
from endpoints.instantiations.agencies_.put.dto import AgencyInfoPutDTO
from endpoints.instantiations.agencies_.post.dto import AgencyInfoPostDTO
from endpoints.instantiations.agencies_._shared.base import AgencyInfoBaseSchema
from utilities.enums import SourceMappingEnum

def get_agency_info_field(
    schema: type[AgencyInfoBaseSchema],  # pyright: ignore[reportInvalidTypeForm]
    nested_dto_class: type[Union[AgencyInfoPutDTO, AgencyInfoPostDTO]],
) -> fields.Nested:
    return fields.Nested(
        schema,
        required=True,
        metadata={
            "description": "Information about the agency",
            "source": SourceMappingEnum.JSON,
            "nested_dto_class": nested_dto_class,
        },
    )
