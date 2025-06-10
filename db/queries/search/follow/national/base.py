from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.implementations.core.record.type import RecordType
from db.models.implementations.core.record.category import RecordCategory
from middleware.enums import RecordTypes
from utilities.enums import RecordCategories


class FollowNationalBaseQueryBuilder:

    def __init__(
        self,
    ):
        pass

    def get_record_type_ids_from_record_types(
        self, session: Session, record_types: list[RecordTypes]
    ) -> list[int]:
        rt_str_list = [rt.value for rt in record_types]
        query = select(RecordType.id).where(RecordType.name.in_(rt_str_list))

        results = session.execute(query).scalars().all()
        return results

    def get_record_type_ids_from_record_categories(
        self, session: Session, record_categories: list[RecordCategories]
    ) -> list[int]:
        rc_str_list = [rc.value for rc in record_categories]
        query = (
            select(RecordType.id)
            .join(RecordCategory, RecordCategory.id == RecordType.category_id)
            .where(RecordCategory.name.in_(rc_str_list))
        )

        results = session.execute(query).scalars().all()
        return results
