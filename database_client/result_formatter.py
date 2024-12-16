from collections import namedtuple
from typing import Any, Optional

from sqlalchemy import RowMapping
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.inspection import inspect

from database_client.constants import (
    DATA_SOURCES_MAP_COLUMN,
    METADATA_METHOD_NAMES,
)
from database_client.db_client_dataclasses import WhereMapping
from database_client.models import SQL_ALCHEMY_TABLE_REFERENCE
from database_client.subquery_logic import SubqueryParameters
from utilities.common import format_arrays


class ResultFormatter:
    """
    Formats results for specific database queries
    Coupled with the DatabaseClient class, whose outputs are formatted here
    """

    @staticmethod
    def tuples_to_column_value_dict(
        columns: list[str], tuples: list[tuple]
    ) -> list[dict]:
        """
        Combine a list of output columns with a list of results,
        and produce a list of dictionaries where the keys correspond
        to the output columns and the values correspond to the results
        :param columns:
        :param tuples:
        :return:
        """
        zipped_results = [dict(zip(columns, result)) for result in tuples]
        formatted_results = []
        for zipped_result in zipped_results:
            formatted_results.append(format_arrays(zipped_result))
        return formatted_results

    @staticmethod
    def zip_get_datas_sources_for_map_results(results: list[tuple]) -> list[dict]:
        return ResultFormatter.tuples_to_column_value_dict(
            DATA_SOURCES_MAP_COLUMN, results
        )

    @staticmethod
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


def dictify_namedtuple(result: list[namedtuple]) -> list[dict[str, Any]]:
    return [result._asdict() for result in result]
