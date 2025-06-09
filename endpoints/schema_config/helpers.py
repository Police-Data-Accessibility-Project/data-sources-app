from typing import Type, Optional

from marshmallow import Schema

from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.primary_resource_logic.user_queries import (
    UserRequestSchema,
    UserRequestDTO,
)
from middleware.schema_and_dto.dtos.agencies.related_agency_by_id import (
    RelatedAgencyByIDDTO,
)
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.schema_and_dto.dtos.search.request import SearchRequestsDTO
from middleware.schema_and_dto.dtos.typeahead import TypeaheadDTO
from middleware.schema_and_dto.schemas.common.base import GetByIDBaseSchema
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    IDAndMessageSchema,
    MessageSchema,
)
from middleware.schema_and_dto.schemas.data_sources.related_agency.by_id import (
    RelatedAgencyByIDSchema,
)
from middleware.schema_and_dto.schemas.search.request import SearchRequestSchema
from middleware.schema_and_dto.schemas.typeahead.request import TypeaheadQuerySchema
from middleware.schema_and_dto.types import DTOTypes


def get_post_resource_endpoint_schema_config(
    input_schema: Schema,
    input_dto_class: Type[DTOTypes],
) -> EndpointSchemaConfig:
    return EndpointSchemaConfig(
        input_schema=input_schema,
        primary_output_schema=IDAndMessageSchema(),
        input_dto_class=input_dto_class,
    )


def get_put_resource_endpoint_schema_config(
    input_schema: Schema,
    input_dto_class: Optional[Type[DTOTypes]] = None,
) -> EndpointSchemaConfig:
    return schema_config_with_message_output(
        input_schema=input_schema,
        input_dto_class=input_dto_class,
    )


def get_get_by_id_endpoint_schema_config(
    primary_output_schema: Schema,
) -> EndpointSchemaConfig:
    return EndpointSchemaConfig(
        input_schema=GetByIDBaseSchema(),
        input_dto_class=GetByIDBaseDTO,
        primary_output_schema=primary_output_schema,
    )


def get_typeahead_schema_config(
    primary_output_schema: Schema,
) -> EndpointSchemaConfig:
    return EndpointSchemaConfig(
        input_schema=TypeaheadQuerySchema(),
        input_dto_class=TypeaheadDTO,
        primary_output_schema=primary_output_schema,
    )


def get_user_request_endpoint_schema_config(
    primary_output_schema: Schema,
) -> EndpointSchemaConfig:
    return EndpointSchemaConfig(
        input_schema=UserRequestSchema(),
        input_dto_class=UserRequestDTO,
        primary_output_schema=primary_output_schema,
    )


def schema_config_with_message_output(
    input_schema: Optional[Schema] = None,
    input_dto_class: Optional[Type[DTOTypes]] = None,
):
    return EndpointSchemaConfig(
        input_schema=input_schema,
        primary_output_schema=MessageSchema(),
        input_dto_class=input_dto_class,
    )


DELETE_BY_ID = schema_config_with_message_output(
    input_schema=GetByIDBaseSchema(),
)
DATA_SOURCES_RELATED_AGENCY_BY_ID = EndpointSchemaConfig(
    input_schema=RelatedAgencyByIDSchema(), input_dto_class=RelatedAgencyByIDDTO
)
SEARCH_FOLLOW_UPDATE = EndpointSchemaConfig(
    input_schema=SearchRequestSchema(
        exclude=["record_categories", "output_format"],
    ),
    input_dto_class=SearchRequestsDTO,
)
