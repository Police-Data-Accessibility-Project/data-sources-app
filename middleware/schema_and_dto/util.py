from typing import Any

from utilities.enums import SourceMappingEnum


def get_json_metadata(description: str, **kwargs: dict) -> dict[str, Any]:
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

