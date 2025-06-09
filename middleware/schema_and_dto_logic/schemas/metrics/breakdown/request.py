from marshmallow import Schema, validate, fields

from db.constants import GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS
from middleware.schema_and_dto_logic.schemas.common.fields import (
    PAGE_FIELD,
    SORT_ORDER_FIELD,
)
from utilities.enums import SourceMappingEnum


class MetricsFollowedSearchesBreakdownRequestSchema(Schema):
    page = PAGE_FIELD
    sort_by = fields.Str(
        required=False,
        metadata={
            "description": f"The field to sort the results by. "
            f"Sortable fields are: {', '.join(GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS)}",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
        validate=validate.OneOf(
            GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS
        ),
    )
    sort_order = SORT_ORDER_FIELD
