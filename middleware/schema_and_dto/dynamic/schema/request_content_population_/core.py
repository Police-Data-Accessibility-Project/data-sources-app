from pydantic import BaseModel

from middleware.schema_and_dto.dynamic.schema.request_content_population_.helpers import \
    get_source_data_info_from_sources, validate_data, _apply_transformation_functions_to_dict, setup_dto_class
from middleware.schema_and_dto.types import SchemaTypes


def populate_schema_with_request_content(
    schema: SchemaTypes, dto_class: type[BaseModel], load_file: bool = False
) -> BaseModel:
    """
    Populates a marshmallow schema with request content, given custom arguments in the schema fields
    Custom arguments include:
    * source: The source in the request the data will be pulled from
    * transformation_function (optional): A function that will be applied to the data
    :param schema_class:
    :param dto_class:
    :return:
    """
    # Get all declared fields from the schema
    if load_file:
        raise NotImplementedError("Load file logic has been removed")
    fields = schema.fields
    source_data_info = get_source_data_info_from_sources(schema)
    intermediate_data = validate_data(source_data_info.data, schema)
    _apply_transformation_functions_to_dict(fields, intermediate_data)

    return setup_dto_class(
        data=intermediate_data,
        dto_class=dto_class,
        nested_dto_info_list=source_data_info.nested_dto_info_list,
    )
