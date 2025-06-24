from sqlalchemy import select

from db.models.implementations.core.record.type import RecordType
from db.queries.builder_.core import QueryBuilderBase


class RecordTypeMixin:

    def _get_record_type_id(
        self: QueryBuilderBase,
        record_type_name: str
    ) -> int:
        query = (
            select(RecordType.id)
            .where(
                RecordType.name == record_type_name
            )
        )
        return self.session.execute(query).fetchone()[0]
