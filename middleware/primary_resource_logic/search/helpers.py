from csv import DictWriter
from io import BytesIO, StringIO
from typing import Optional

from flask import make_response, send_file
from werkzeug.exceptions import BadRequest

from middleware.enums import JurisdictionSimplified, OutputFormatEnum
from middleware.util.datetime import get_datetime_now
from utilities.enums import RecordCategories


def get_jurisdiction_type_enum(
    jurisdiction_type_str: str,
) -> Optional[JurisdictionSimplified]:
    if jurisdiction_type_str in [
        "local",
        "school",
        "military",
        "tribal",
        "transit",
        "port",
    ]:
        return JurisdictionSimplified.LOCALITY
    return JurisdictionSimplified(jurisdiction_type_str)


def format_search_results(search_results: list[dict]) -> dict:
    """
    Convert results to the following format:

    {
      "count": <number>,
      "data": {
          "federal": {
            "count": <number>,
            "results": [<data-source-record>]
          }
          "state": {
            "count": <number>,
            "results": [<data-source-record>]
          },
          county: {
            "count": <number>,
            "results": [<data-source-record>]
          },
          locality: {
            "count": <number>,
            "results": [<data-source-record>]
          },
        }
    }

    :param search_results:
    :return:
    """

    response = {"count": 0, "data": {}}

    data = response["data"]
    # Create sub-dictionary for each jurisdiction
    for jurisdiction in [j.value for j in JurisdictionSimplified]:
        data[jurisdiction] = {"count": 0, "results": []}

    for result in search_results:
        jurisdiction_str = result.get("jurisdiction_type")
        jurisdiction = get_jurisdiction_type_enum(jurisdiction_str)
        data[jurisdiction.value]["count"] += 1
        data[jurisdiction.value]["results"].append(result)
        response["count"] += 1

    return response


def format_as_csv(ld: list[dict]) -> BytesIO:
    string_output = StringIO()
    writer = DictWriter(string_output, fieldnames=list(ld[0].keys()))
    writer.writeheader()
    writer.writerows(ld)
    string_output.seek(0)
    bytes_output = string_output.getvalue().encode("utf-8")
    return BytesIO(bytes_output)


def create_search_record(access_info, db_client, dto):
    db_client.create_search_record(
        user_id=access_info.get_user_id(),
        location_id=dto.location_id,
        # Pass originally provided record categories
        record_categories=dto.record_categories,
        record_types=dto.record_types,
    )


def send_search_results(search_results: list[dict], output_format: OutputFormatEnum):
    if output_format == OutputFormatEnum.JSON:
        return send_as_json(search_results)
    if output_format == OutputFormatEnum.CSV:
        return send_as_csv(search_results)
    raise BadRequest("Invalid output format.")


def send_as_json(search_results):
    formatted_search_results = format_search_results(search_results)
    return make_response(formatted_search_results)


def send_as_csv(search_results):
    filename = f"search_results-{get_datetime_now()}.csv"
    csv_stream = format_as_csv(ld=search_results)
    return send_file(
        csv_stream, download_name=filename, mimetype="text/csv", as_attachment=True
    )


def get_explicit_record_categories(
    record_categories=Optional[list[RecordCategories]],
) -> Optional[list[RecordCategories]]:
    if record_categories is None:
        return None
    if RecordCategories.ALL in record_categories:
        if len(record_categories) > 1:
            raise BadRequest("ALL cannot be provided with other record categories.")
        return [rc for rc in RecordCategories if rc != RecordCategories.ALL]
    return record_categories
