from typing import Optional, Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.implementations.core.record.category import RecordCategory
from db.models.implementations.core.record.type import RecordType
from db.queries.builder.core import QueryBuilderBase
from middleware.enums import RecordTypesEnum
from utilities.enums import RecordCategoryEnum


class FollowBaseQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        location_id: int,
        user_id: int,
        record_types: Optional[list[RecordTypesEnum]],
        record_categories: Optional[list[RecordCategoryEnum]],
    ):
        super().__init__()
        self.location_id = location_id
        self.user_id = user_id
        self.record_categories = record_categories
        # If none of the record types or categories are specified, get all
        if record_types is None and self.record_categories is None:
            self.all_record_types = True
            self.record_types = [e for e in RecordTypesEnum]
        else:
            self.all_record_types = False
            self.record_types = record_types
        self.record_type_ids = None

    def setup(self):
        self.record_type_ids = self.get_record_type_ids(
            record_types=self.record_types, record_categories=self.record_categories
        )

    def build(self, session: Session) -> Any:
        self._session = session
        self.setup()
        return self.run()

    def get_record_type_ids_from_record_types(
        self, record_types: Optional[list[RecordTypesEnum]]
    ) -> list[int]:
        if record_types is None:
            return []

        rt_str_list = [rt.value for rt in record_types]
        query = select(RecordType.id).where(RecordType.name.in_(rt_str_list))

        results = self.execute(query).scalars().all()
        return list(results)

    def get_record_type_ids_from_record_categories(
        self, record_categories: Optional[list[RecordCategoryEnum]]
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
        record_types: Optional[list[RecordTypesEnum]],
        record_categories: Optional[list[RecordCategoryEnum]],
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
