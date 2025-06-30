from sqlalchemy import select, func, desc

from db.models.implementations.core.log.table_count import TableCountLog
from db.queries.builder.core import QueryBuilderBase
from middleware.miscellaneous.table_count_logic import TableCountReferenceManager


class GetMostRecentLoggedTableCountsQueryBuilder(QueryBuilderBase):
    def __init__(self):
        super().__init__()

    def run(self) -> TableCountReferenceManager:
        # Get the most recent table count for all distinct tables
        subquery = select(
            TableCountLog.table_name,
            TableCountLog.count,
            func.row_number()
            .over(
                partition_by=TableCountLog.table_name,
                order_by=desc(TableCountLog.created_at),
            )
            .label("row_num"),
        ).subquery()

        stmt = select(subquery.c.table_name, subquery.c.count).where(
            subquery.c.row_num == 1
        )

        results = self.session.execute(stmt).all()
        tcr = TableCountReferenceManager()
        for result in results:
            tcr.add_table_count(
                table_name=result[0],
                count=result[1],
            )
        return tcr
