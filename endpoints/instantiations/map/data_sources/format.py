from db.constants import DATA_SOURCES_MAP_COLUMN
from utilities.common import format_arrays


def zip_get_datas_sources_for_map_results(results: list[tuple]) -> list[dict]:
    return tuples_to_column_value_dict(DATA_SOURCES_MAP_COLUMN, results)


def tuples_to_column_value_dict(columns: list[str], tuples: list[tuple]) -> list[dict]:
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
