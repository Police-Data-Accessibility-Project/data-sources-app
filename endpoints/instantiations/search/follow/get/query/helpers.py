from collections import defaultdict

from db.models.implementations.core.record.type import RecordType


def build_record_category_type_dictionary(
    record_types: list[RecordType]
) -> dict[str, list[str]]:
    d = defaultdict(list)
    for rt in record_types:
        rc = rt.record_category.name
        d[rc].append(rt.name)
    return d
