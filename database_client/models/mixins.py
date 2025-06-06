from typing import Optional

from sqlalchemy.ext.hybrid import hybrid_method


class CountMetadata:
    @hybrid_method
    def count(
        cls,
        data: list[dict],
        **kwargs,
    ) -> int:
        return {"count": len(data)}


class CountSubqueryMetadata:
    @hybrid_method
    def count_subquery(
        cls, data: list[dict], subquery_parameters, **kwargs
    ) -> Optional[dict[str, int]]:
        if not subquery_parameters or len(data) != 1:
            return None

        subquery_counts = {}
        for subquery_param in subquery_parameters:
            linking_column = subquery_param.linking_column
            key = linking_column + "_count"
            count = len(data[0][linking_column])
            subquery_counts.update({key: count})

        return subquery_counts
