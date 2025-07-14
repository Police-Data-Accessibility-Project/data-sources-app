from typing import Optional

from middleware.enums import RecordTypes
from utilities.common import get_enums_from_string
from utilities.enums import RecordCategoryEnum, SourceMappingEnum, ParserLocation


def transform_record_categories(value: str) -> Optional[list[RecordCategoryEnum]]:
    if value is not None:
        return get_enums_from_string(  # pyright: ignore[reportReturnType]
            RecordCategoryEnum, value, case_insensitive=True
        )
    return None


def transform_record_types(value: str) -> Optional[list[RecordTypes]]:
    if value is not None:
        return get_enums_from_string(  # pyright: ignore[reportReturnType]
            RecordTypes, value, case_insensitive=True
        )
    return None


RECORD_CATEGORY_METADATA = {
    "transformation_function": transform_record_categories,
    "description": "The record categories of the search. If empty, all categories will be searched."
    "Multiple record categories can be provided as a comma-separated list, eg. 'Police & Public "
    "Interactions,Agency-published Resources'."
    "Allowable record categories include: \n  * "
    + "\n  * ".join([e.value for e in RecordCategoryEnum]),
    "source": SourceMappingEnum.QUERY_ARGS,
    "location": ParserLocation.QUERY.value,
}
RECORD_TYPE_METADATA = {
    "transformation_function": transform_record_types,
    "description": "The record types of the search. If empty, all types will be searched."
    "Multiple record types can be provided as a comma-separated list, eg. 'Accident Reports,"
    "Stops'. Mutually exclusive with `record_categories`.",
    "source": SourceMappingEnum.QUERY_ARGS,
    "location": ParserLocation.QUERY.value,
}
