from typing import Any, Callable, Optional

from flask import request

from middleware.schema_and_dto_logic.exceptions import MissingArgumentError
from middleware.schema_and_dto_logic.types import SchemaTypes
from utilities.enums import SourceMappingEnum


def _get_required_argument(
    argument_name: str,
    metadata: dict,
    schema_class: SchemaTypes,
    field_name: Optional[str] = None,
) -> Any:
    try:
        return metadata[argument_name]
    except KeyError:
        name = field_name if field_name else schema_class.__name__
        raise MissingArgumentError(
            f"The argument {argument_name} must be specified as a metadata argument in class {name} (as in `Fields.Str(metadata={argument_name}:value`)"
        )


def _get_source_getting_function(source: SourceMappingEnum) -> Callable:
    # TODO: Consider moving this to separate map variable,
    #        rather than define within the function
    source_mapping: dict[SourceMappingEnum, Callable] = {
        SourceMappingEnum.QUERY_ARGS: request.args.get,
        SourceMappingEnum.FORM: request.form.get,
        SourceMappingEnum.JSON: lambda key: (
            request.json.get(key) if request.json else None
        ),
        SourceMappingEnum.PATH: request.view_args.get,
        SourceMappingEnum.FILE: request.files.get,
    }
    return source_mapping[source]


def get_json_metadata(description: str, **kwargs) -> dict:
    return {
        "description": description,
        "source": SourceMappingEnum.JSON,
        **kwargs,
    }


def get_query_metadata(description: str, **kwargs) -> dict:
    return {
        "description": description,
        "source": SourceMappingEnum.QUERY_ARGS,
        **kwargs,
    }


def get_path_metadata(description: str, **kwargs) -> dict:
    return {
        "description": description,
        "source": SourceMappingEnum.PATH,
        **kwargs,
    }
