from http import HTTPStatus

from marshmallow import Schema


class OutputSchemaManager:
    def __init__(self, output_schemas: dict[HTTPStatus, Schema]):
        self.output_schemas = output_schemas

    def get_output_schema(self, status_code: HTTPStatus) -> Schema:
        return self.output_schemas.get(status_code, None)

    def get_output_schemas(self) -> dict[HTTPStatus, Schema]:
        return self.output_schemas
