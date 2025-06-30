import datetime
from typing import Optional

from sqlalchemy import func, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr

from db.models.helpers import iter_with_special_cases
from db.models.types import timestamp


class CountMetadata:
    @hybrid_method
    def count(
        cls,
        data: list[dict],
        **kwargs,
    ) -> int:
        return {"count": len(data)}


class CountSubqueryMetadata:
    @hybrid_method
    def count_subquery(
        cls, data: list[dict], subquery_parameters, **kwargs
    ) -> Optional[dict[str, int]]:
        if not subquery_parameters or len(data) != 1:
            return None

        subquery_counts = {}
        for subquery_param in subquery_parameters:
            linking_column = subquery_param.linking_column
            key = linking_column + "_count"
            count = len(data[0][linking_column])
            subquery_counts.update({key: count})

        return subquery_counts


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )


class UpdatedAtMixin:
    updated_at: Mapped[timestamp] = mapped_column(
        server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )


class UserIDMixin:
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))

    @declared_attr
    def user(cls: type["UserIDMixin"]) -> Mapped["User"]:
        return relationship(
            "User",
            primaryjoin=f"foreign({cls.__name__}.user_id) == User.id",
            uselist=False,
        )


class LocationIDMixin:
    location_id: Mapped[int] = mapped_column(ForeignKey("public.locations.id"))

    @declared_attr
    def location(cls: type["LocationIDMixin"]) -> Mapped["Location"]:
        return relationship(
            "Location",
            primaryjoin=f"foreign({cls.__name__}.location_id) == Location.id",
            uselist=False,
        )


class DataRequestIDMixin:
    data_request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))

    @declared_attr
    def data_request(cls: type["DataRequestIDMixin"]) -> Mapped["DataRequest"]:
        return relationship(
            "DataRequest",
            primaryjoin=f"foreign({cls.__name__}.data_request_id) == DataRequest.id",
            uselist=False,
        )


class DataSourceIDMixin:
    data_source_id: Mapped[int] = mapped_column(ForeignKey("public.data_sources.id"))

    @declared_attr
    def data_source(cls: type["DataSourceIDMixin"]) -> Mapped["DataSource"]:
        return relationship(
            "DataSource",
            primaryjoin=f"foreign({cls.__name__}.data_source_id) == DataSource.id",
            uselist=False,
        )


class RecordTypeIDMixin:
    record_type_id: Mapped[int] = mapped_column(ForeignKey("public.record_types.id"))

    @declared_attr
    def record_type(cls: type["RecordTypeIDMixin"]) -> Mapped["RecordType"]:
        return relationship(
            "RecordType",
            primaryjoin=f"foreign({cls.__name__}.record_type_id) == RecordType.id",
            uselist=False,
        )


class IterWithSpecialCasesMixin:
    special_cases: Optional[dict] = None

    def __iter__(self):
        yield from iter_with_special_cases(self, special_cases=self.special_cases)
