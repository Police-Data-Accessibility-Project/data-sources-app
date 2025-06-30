from csv import DictWriter
from typing import TextIO

from marshmallow import Schema


class TestCSVCreator:
    def __init__(self, schema: Schema):
        self.fields = schema.fields

    def create_csv(self, file: TextIO, rows: list[dict]):
        header = list(self.fields.keys())
        writer = DictWriter(file, fieldnames=header)
        # Write header row using header
        writer.writerow({field: field for field in header})

        for row in rows:
            writer.writerow(row)
        file.close()
