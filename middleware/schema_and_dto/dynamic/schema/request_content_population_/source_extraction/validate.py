from werkzeug.exceptions import BadRequest


def validate_fields(
    expected_fields: list[str],
    actual_fields: list[str]
) -> None:
    unexpected_fields = set(actual_fields) - set(expected_fields)
    if len(unexpected_fields) > 0:
        raise BadRequest(f"Unexpected fields: {unexpected_fields}")