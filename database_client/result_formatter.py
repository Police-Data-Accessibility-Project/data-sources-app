from collections import namedtuple
from typing import Any

from database_client.constants import (
    DATA_SOURCES_APPROVED_COLUMNS,
    DATA_SOURCES_MAP_COLUMN,
    DATA_SOURCES_OUTPUT_COLUMNS,
    AGENCY_APPROVED_COLUMNS,
)
from utilities.common import convert_dates_to_strings, format_arrays


class ResultFormatter:
    """
    Formats results for specific database queries
    Coupled with the DatabaseClient class, whose outputs are formatted here
    """

    @staticmethod
    def convert_data_source_matches(
        data_source_output_columns: list[str], results: list[tuple]
    ) -> list[dict]:
        """
        Combine a list of output columns with a list of results,
        and produce a list of dictionaries where the keys correspond
        to the output columns and the values correspond to the results
        :param data_source_output_columns:
        :param results:
        :return:
        """
        data_source_matches = [
            dict(zip(data_source_output_columns, result)) for result in results
        ]
        data_source_matches_converted = []
        for data_source_match in data_source_matches:
            data_source_match = convert_dates_to_strings(data_source_match)
            data_source_matches_converted.append(format_arrays(data_source_match))
        return data_source_matches_converted

    @staticmethod
    def zip_needs_identification_data_source_results(
        results: list[tuple],
    ) -> list[dict]:
        return ResultFormatter.convert_data_source_matches(
            DATA_SOURCES_APPROVED_COLUMNS, results
        )

    @staticmethod
    def zip_get_datas_sources_for_map_results(results: list[tuple]) -> list[dict]:
        return ResultFormatter.convert_data_source_matches(
            DATA_SOURCES_MAP_COLUMN, results
        )

    @staticmethod
    def zip_get_approved_data_sources_results(results: list[tuple]) -> list[dict]:
        return ResultFormatter.convert_data_source_matches(
            DATA_SOURCES_OUTPUT_COLUMNS, results
        )

    @staticmethod
    def zip_get_data_source_by_id_results(results: tuple[Any, ...]) -> dict[str, Any]:
        data_source_and_agency_columns = (
            DATA_SOURCES_APPROVED_COLUMNS + AGENCY_APPROVED_COLUMNS
        )
        data_source_and_agency_columns.extend(
            ["data_source_id", "agency_id", "agency_name"]
        )
        # Convert to a list and only return the first (and only)
        return ResultFormatter.convert_data_source_matches(
            data_source_and_agency_columns, [results]
        )[0]

def dictify_namedtuple(result: list[namedtuple]) -> list[dict[str, Any]]:
    return [result._asdict() for result in result]