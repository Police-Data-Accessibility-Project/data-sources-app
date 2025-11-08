from typing import Sequence

from sqlalchemy import select, RowMapping

from db.helpers_.record_type.mapper import RecordTypeMapper
from db.helpers_.record_type.mapping import RecordTypeMapping
from db.models.implementations.core.record.category import RecordCategory
from db.models.implementations.core.record.type import RecordType
from db.queries.builder.core import QueryBuilderBase
from middleware.enums import RecordTypesEnum
from utilities.enums import RecordCategoryEnum


class GetRecordTypeMapperQueryBuilder(QueryBuilderBase):

    def run(self) -> RecordTypeMapper:
        query = (
            select(
                RecordType.id,
                RecordType.name,
                RecordType.category_id,
                RecordCategory.name,
            )
            .join(
                RecordCategory,
                RecordType.category_id == RecordCategory.id,
            )
        )

        raw_results: Sequence[RowMapping] = self.mappings(query)

        mappings: list[RecordTypeMapping] = []
        for raw_result in raw_results:
            mapping = RecordTypeMapping(
                record_type_id=raw_result[RecordType.id],
                record_type=RecordTypesEnum(raw_result[RecordType.name]),
                record_category_id=raw_result[RecordType.category_id],
                record_category=RecordCategoryEnum(raw_result[RecordCategory.name]),
            )
            mappings.append(mapping)

        return RecordTypeMapper(mappings)


