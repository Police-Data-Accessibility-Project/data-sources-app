from typing import Callable

from flask import request


from utilities.enums import SourceMappingEnum


def _get_source_getting_function(source: SourceMappingEnum) -> Callable:
    source_function_mapping: dict[SourceMappingEnum, Callable] = {
        SourceMappingEnum.QUERY_ARGS: request.args.get,
        SourceMappingEnum.FORM: request.form.get,
        SourceMappingEnum.JSON: lambda key: (
            request.json.get(key) if request.json else None
        ),
        SourceMappingEnum.PATH: request.view_args.get,  # pyright: ignore[reportOptionalMemberAccess]
        SourceMappingEnum.FILE: request.files.get,
    }

    return source_function_mapping[source]
