from sqlalchemy.orm import Session

from db.queries.builder import QueryBuilderBase


class FollowBaseQueryBuilder(QueryBuilderBase):

    def __init__(self, dto: SearchFollowNationalRequestDTO, session: Session):
        super().__init__(session)
        self.record_type_ids = self.get_record_type_ids(dto)

    def get_record_type_ids_from_record_types(
        self, record_types: list[RecordTypes]
    ) -> list[int]:
        rt_str_list = [rt.value for rt in record_types]
        query = select(RecordType.id).where(RecordType.name.in_(rt_str_list))

        results = self.execute(query).scalars().all()
        return list(results)

    def get_record_type_ids_from_record_categories(
        self, record_categories: list[RecordCategories]
    ) -> list[int]:
        rc_str_list = [rc.value for rc in record_categories]
        query = (
            select(RecordType.id)
            .join(RecordCategory, RecordCategory.id == RecordType.category_id)
            .where(RecordCategory.name.in_(rc_str_list))
        )

        results = self.execute(query).scalars().all()
        return list(results)

    def get_record_type_ids(self, dto: SearchFollowNationalRequestDTO) -> list[int]:
        if dto.record_types is not None:
            record_type_ids = self.get_record_type_ids_from_record_types(
                record_types=dto.record_types
            )
        else:
            record_type_ids = self.get_record_type_ids_from_record_categories(
                record_categories=dto.record_categories
            )

        return record_type_ids
