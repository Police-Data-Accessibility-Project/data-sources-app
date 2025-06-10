from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.implementations.core.record.category import RecordCategory
from db.models.implementations.core.record.type import RecordType
from db.queries.builder import QueryBuilderBase
from middleware.enums import RecordTypes
from utilities.enums import RecordCategories


class FollowBaseQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        location_id: int,
        user_id: int,
        record_types: list[RecordTypes],
        record_categories: list[RecordCategories],
        session: Session,
    ):
        super().__init__(session)
        self.location_id = location_id
        self.user_id = user_id
        self.record_type_ids = self.get_record_type_ids(
            record_types=record_types, record_categories=record_categories
        )

    def get_record_type_ids_from_record_types(
        self, record_types: Optional[list[RecordTypes]]
    ) -> list[int]:
        if record_types is None:
            return []

        rt_str_list = [rt.value for rt in record_types]
        query = select(RecordType.id).where(RecordType.name.in_(rt_str_list))

        results = self.execute(query).scalars().all()
        return list(results)

    def get_record_type_ids_from_record_categories(
        self, record_categories: Optional[list[RecordCategories]]
    ) -> list[int]:
        if record_categories is None:
            return []

        rc_str_list = [rc.value for rc in record_categories]
        query = (
            select(RecordType.id)
            .join(RecordCategory, RecordCategory.id == RecordType.category_id)
            .where(RecordCategory.name.in_(rc_str_list))
        )

        results = self.execute(query).scalars().all()
        return list(results)

    def get_record_type_ids(
        self,
        record_types: Optional[list[RecordTypes]],
        record_categories: Optional[list[RecordCategories]],
    ) -> list[int]:
        if record_types is not None:
            record_type_ids = self.get_record_type_ids_from_record_types(
                record_types=record_types
            )
        else:
            record_type_ids = self.get_record_type_ids_from_record_categories(
                record_categories=record_categories
            )

        return record_type_ids
