from http import HTTPStatus
from typing import Optional, Type

from marshmallow import Schema
from pydantic import BaseModel

from endpoints.schema_config.config.manager import OutputSchemaManager
from middleware.schema_and_dto.non_dto_dataclasses import SchemaPopulateParameters


class EndpointSchemaConfig:
    def __init__(
        self,
        input_schema: Optional[Schema] = None,
        primary_output_schema: Optional[Schema] = None,
        input_dto_class: Optional[Type[BaseModel]] = None,
        additional_output_schemas: Optional[dict[HTTPStatus, Schema]] = None,
    ):
        """

        :param input_schema: Describes the schema to be input on a request
        :param primary_output_schema: Describes the schema to be output on a successful request
        :param input_dto_class: Describes the DTO which will be populated based on the input schema.
        """
        self.input_schema = input_schema
        self.primary_output_schema = primary_output_schema
        self.input_dto_class = input_dto_class
        all_output_schemas = {}
        if primary_output_schema is not None:
            all_output_schemas[HTTPStatus.OK] = primary_output_schema
        if additional_output_schemas is not None:
            all_output_schemas.update(additional_output_schemas)
        self.output_schema_manager = OutputSchemaManager(
            output_schemas=all_output_schemas
        )

    def get_schema_populate_parameters(self) -> SchemaPopulateParameters:
        if "file" in self.input_schema.fields:
            load_file = True
        else:
            load_file = False
        return SchemaPopulateParameters(
            schema=self.input_schema,
            dto_class=self.input_dto_class,
            load_file=load_file,
        )
