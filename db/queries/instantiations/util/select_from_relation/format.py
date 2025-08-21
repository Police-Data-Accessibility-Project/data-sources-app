from typing import Optional, Any

from sqlalchemy import inspect
from sqlalchemy.ext.hybrid import hybrid_method

from db.constants import METADATA_METHOD_NAMES
from db.models.table_reference import SQL_ALCHEMY_TABLE_REFERENCE
from db.subquery_logic import SubqueryParameters


def format_with_metadata(
    data: list[dict],
    relation_name: str,
    subquery_parameters: Optional[list[SubqueryParameters]] = [],
) -> dict[str, Any]:
    metadata_dict = {}
    relation_reference = SQL_ALCHEMY_TABLE_REFERENCE[relation_name]

    # Iterate through all properties of the Table
    for name, descriptor in inspect(relation_reference).all_orm_descriptors.items():
        # Retrieve and call the metadata method
        if type(descriptor) != hybrid_method or name not in METADATA_METHOD_NAMES:
            continue
        metadata_result = getattr(relation_reference, name)(
            data=data,
            subquery_parameters=subquery_parameters,
        )
        if metadata_result is not None:
            metadata_dict.update(metadata_result)

    return {
        "metadata": metadata_dict,
        "data": data,
    }
