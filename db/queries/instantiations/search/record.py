from typing import Optional, Union, Any

from sqlalchemy import insert, select

from db.models.implementations import (
    LinkRecentSearchRecordTypes,
    LinkRecentSearchRecordCategories,
)
from db.models.implementations.core.recent_search.core import RecentSearch
from db.models.implementations.core.record.category import RecordCategory
from db.models.implementations.core.record.type import RecordType
from db.queries.builder.core import QueryBuilderBase
from middleware.enums import RecordTypes
from utilities.enums import RecordCategories


class CreateSearchRecordQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        user_id: int,
        location_id: int,
        record_categories: Optional[
            Union[list[RecordCategories], RecordCategories]
        ] = None,
        record_types: Optional[Union[list[RecordTypes], RecordTypes]] = None,
    ):
        super().__init__()
        self.user_id = user_id
        self.location_id = location_id
        self.record_categories = record_categories
        self.record_types = record_types

    def run(self) -> Any:
        if isinstance(self.record_categories, RecordCategories):
            self.record_categories = [self.record_categories]

        with self.session.begin():
            # Insert into recent_search table and get recent_search_id
            query = (
                insert(RecentSearch)
                .values({"user_id": self.user_id, "location_id": self.location_id})
                .returning(RecentSearch.id)
            )
            result = self.session.execute(query)
            recent_search_id = result.one()[0]

            if self.record_categories is not None:
                self.insert_record_category_search_records(
                    recent_search_id, self.record_categories
                )
            if self.record_types is not None:
                self.insert_record_type_search_records(
                    recent_search_id, self.record_types
                )

    def insert_record_type_search_records(self, recent_search_id, record_types):
        # For all record types, insert into link table
        for record_type in record_types:
            query = select(RecordType).filter(RecordType.name == record_type.value)
            rt_id = self.session.execute(query).fetchone()[0].id

            query = insert(LinkRecentSearchRecordTypes).values(
                {"recent_search_id": recent_search_id, "record_type_id": rt_id}
            )
            self.session.execute(query)

    def insert_record_category_search_records(
        self, recent_search_id, record_categories
    ):
        # For all record types, insert into link table
        for record_type in record_categories:
            query = select(RecordCategory).filter(
                RecordCategory.name == record_type.value
            )
            rc_id = self.session.execute(query).fetchone()[0].id

            query = insert(LinkRecentSearchRecordCategories).values(
                {"recent_search_id": recent_search_id, "record_category_id": rc_id}
            )
            self.session.execute(query)
