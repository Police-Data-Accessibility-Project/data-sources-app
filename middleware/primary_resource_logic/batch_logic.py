from io import BytesIO

from marshmallow import Schema

from database_client.database_client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_csv_to_schema_conversion_logic import SchemaUnflattener
from middleware.schema_and_dto_logic.primary_resource_dtos.batch_dtos import BatchRequestDTO
from csv import DictReader


def replace_empty_strings_with_none(row: dict):
    for key, value in row.items():
        if value == "":
            row[key] = None


def get_rows_from_csv(
    file: BytesIO,
    schema: Schema
):
    # Get rows from csv
    text_file = (line.decode('utf-8') for line in file)

    reader = DictReader(text_file)
    rows = list(reader)
    loaded_rows = []
    for row in rows:
        replace_empty_strings_with_none(row)
        loaded_row = schema.load(row)
        loaded_rows.append(loaded_row)
    return loaded_rows



def batch_post_agency(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: BatchRequestDTO
):

    rows = get_rows_from_csv(
        file=dto.file,
        schema=dto.csv_schema
    )
    unflattener = SchemaUnflattener(
        flat_schema_class=dto.csv_schema.__class__
    )

    for row in rows:
        unflattened_row = unflattener.unflatten(flat_data=row)
        pass

    raise NotImplementedError
