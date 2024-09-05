from typing import Type, Any, Callable

from flask import request

from middleware.schema_and_dto_logic.custom_exceptions import MissingArgumentError
from middleware.schema_and_dto_logic.custom_types import SchemaTypes
from utilities.enums import SourceMappingEnum


def _get_required_argument(
    argument_name: str, metadata: dict, schema_class: Type[SchemaTypes]
) -> Any:
    try:
        return metadata[argument_name]
    except KeyError:
        raise MissingArgumentError(
            f"The argument {argument_name} must be specified as a fields argument in class {schema_class.__name__} (as in `Fields.Str({argument_name}=value`)"
        )


def _get_source_getting_function(source: SourceMappingEnum) -> Callable:
    source_mapping: dict[SourceMappingEnum, Callable] = {
        SourceMappingEnum.QUERY_ARGS: request.args.get,
        SourceMappingEnum.FORM: request.form.get,
        SourceMappingEnum.JSON: lambda key: (
            request.json.get(key) if request.json else None
        ),
        SourceMappingEnum.PATH: request.view_args.get,
    }
    return source_mapping[source]
