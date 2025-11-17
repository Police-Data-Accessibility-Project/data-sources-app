from enum import Enum

from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddInnerResponse,
)


def _consolidate_responses(
    request_app_mappings: dict[int, int],
) -> list[SourceManagerSyncAddInnerResponse]:
    inner_responses: list[SourceManagerSyncAddInnerResponse] = []
    for request_id, ds_id in request_app_mappings.items():
        inner_responses.append(
            SourceManagerSyncAddInnerResponse(
                request_id=request_id,
                app_id=ds_id,
            )
        )
    return inner_responses


def _value_if_not_none(value: Enum | None) -> str | None:
    if value is None:
        return None
    return value.value
