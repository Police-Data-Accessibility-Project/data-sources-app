from marshmallow import fields, validate

from db.enums import SortOrder
from utilities.enums import SourceMappingEnum

PAGE_FIELD = fields.Integer(
    validate=validate.Range(min=1),
    load_default=1,
    metadata={
        "description": "The page number of the results to retrieve. Begins at 1.",
        "source": SourceMappingEnum.QUERY_ARGS,
    },
)
SORT_BY_FIELD = fields.Str(
    required=False,
    metadata={
        "description": "The field to sort the results by.",
        "source": SourceMappingEnum.QUERY_ARGS,
    },
)


def get_sort_by_field(allowed_values: list) -> fields.Str:
    return fields.Str(
        required=False,
        metadata={
            "description": f"The field to sort the results by. Sortable fields are: {', '.join(allowed_values)}",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
        validate=validate.OneOf(allowed_values),
    )


SORT_ORDER_FIELD = fields.Enum(
    required=False,
    enum=SortOrder,
    by_value=fields.Str,
    load_default=SortOrder.DESCENDING,
    metadata={
        "source": SourceMappingEnum.QUERY_ARGS,
        "description": "The order to sort the results by.",
    },
)
