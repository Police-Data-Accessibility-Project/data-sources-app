# pyright: reportUninitializedInstanceVariable=false
from datetime import date
from typing import final

from sqlalchemy import Column, DateTime, func, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.enums import (
    AccessType,
    URLStatus,
    AgencyAggregation,
    DetailLevel,
    UpdateMethod,
    RetentionSchedule,
    ApprovalStatus,
)
from db.models.helpers import (
    make_get_iter_model_list_of_dict,
    enum_list_column,
    enum_column,
)
from db.models.implementations.core.location.core import Location
from db.models.mixins import CountMetadata, CreatedAtMixin, IterWithSpecialCasesMixin
from db.models.templates.standard import StandardBase
from db.models.types import (
    text,
    URLStatusLiteral,
    timestamp_tz,
)
from middleware.enums import Relations


@final
class DataSource(
    StandardBase,
    CountMetadata,
    CreatedAtMixin,
    IterWithSpecialCasesMixin,
):
    __tablename__ = Relations.DATA_SOURCES.value

    special_cases = {
        "agencies": make_get_iter_model_list_of_dict("agencies"),
        "data_requests": make_get_iter_model_list_of_dict("data_requests"),
    }

    name: Mapped[str]
    description: Mapped[str | None]
    source_url: Mapped[str | None]
    agency_supplied: Mapped[bool | None]
    supplying_entity: Mapped[str | None]
    agency_originated: Mapped[bool | None]
    agency_aggregation: Mapped[AgencyAggregation | None] = enum_column(
        AgencyAggregation, name="agency_aggregation"
    )
    coverage_start: Mapped[date | None]
    coverage_end: Mapped[date | None]
    updated_at: Mapped[date | None] = Column(DateTime, default=func.now())
    detail_level: Mapped[DetailLevel | None] = enum_column(
        DetailLevel, name="detail_level"
    )
    # Note: Below is an array of enums in Postgres but this is cumbersome to convey in SQLAlchemy terms
    access_types = enum_list_column(AccessType, name="access_type")
    data_portal_type: Mapped[str | None]
    record_formats = Column(ARRAY(String), default=[])
    update_method: Mapped[UpdateMethod | None] = enum_column(
        UpdateMethod, name="update_method"
    )
    tags = Column(ARRAY(String), default=[])
    readme_url: Mapped[str | None]
    originating_entity: Mapped[str | None]
    retention_schedule: Mapped[RetentionSchedule | None] = enum_column(
        RetentionSchedule, name="retention_schedule"
    )
    scraper_url: Mapped[str | None]
    submission_notes: Mapped[str | None]
    rejection_note: Mapped[str | None]
    last_approval_editor: Mapped[int | None]
    submitter_contact_info: Mapped[str | None]
    agency_described_not_in_database: Mapped[str | None]
    data_portal_type_other: Mapped[str | None]
    data_source_request: Mapped[str | None]
    broken_source_url_as_of: Mapped[date | None]
    access_notes: Mapped[text | None]
    url_status: Mapped[URLStatusLiteral] = enum_column(
        URLStatus,
        name="url_status_enum",
        default=URLStatus.OK,
    )
    approval_status: Mapped[ApprovalStatus] = enum_column(
        ApprovalStatus,
        name="approval_status",
        default=ApprovalStatus.PENDING,
    )
    record_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("public.record_types.id")
    )
    approval_status_updated_at: Mapped[timestamp_tz | None]

    # Relationships
    locations: Mapped[list[Location]] = relationship(
        argument="Location",
        secondary="public.link_locations_data_sources_view",
        primaryjoin="LinkLocationDataSourceView.data_source_id == DataSource.id",
        secondaryjoin="LinkLocationDataSourceView.location_id == Location.id",
        back_populates="data_sources",
        viewonly=True,
    )
