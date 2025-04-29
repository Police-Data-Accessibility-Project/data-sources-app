from marshmallow import fields, validate

from database_client.enums import SortOrder
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
