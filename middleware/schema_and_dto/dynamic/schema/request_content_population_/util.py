from typing import Any

from marshmallow import Schema

from middleware.schema_and_dto.exceptions import MissingArgumentError


def _get_required_argument(
    argument_name: str,
    metadata: dict,
    schema_class: Schema,
    field_name: str | None = None,
) -> Any:
    try:
        return metadata[argument_name]
    except KeyError:
        name = field_name if field_name else schema_class.__name__
        raise MissingArgumentError(
            f"The argument {argument_name} must be specified as a metadata argument in class {name} (as in `Fields.Str(metadata={argument_name}:value`)"
        )
