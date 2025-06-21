# pyright: reportUninitializedInstanceVariable=false
from datetime import date
from typing import Optional, get_args

from sqlalchemy import Column, DateTime, func, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, ENUM as pgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.enums import AccessType
from db.models.helpers import make_get_iter_model_list_of_dict
from db.models.implementations.core.location.core import Location
from db.models.mixins import CountMetadata, CreatedAtMixin, IterWithSpecialCasesMixin
from db.models.templates.standard import StandardBase
from db.models.types import (
    AgencyAggregationLiteral,
    DetailLevelLiteral,
    UpdateMethodLiteral,
    RetentionScheduleLiteral,
    text,
    URLStatusLiteral,
    ApprovalStatusLiteral,
    timestamp_tz,
)
from middleware.enums import Relations


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
    description: Mapped[Optional[str]]
    source_url: Mapped[Optional[str]]
    agency_supplied: Mapped[Optional[bool]]
    supplying_entity: Mapped[Optional[str]]
    agency_originated: Mapped[Optional[bool]]
    agency_aggregation: Mapped[Optional[AgencyAggregationLiteral]]
    coverage_start: Mapped[Optional[date]]
    coverage_end: Mapped[Optional[date]]
    updated_at: Mapped[Optional[date]] = Column(DateTime, default=func.now())
    detail_level: Mapped[Optional[DetailLevelLiteral]]
    # Note: Below is an array of enums in Postgres but this is cumbersome to convey in SQLAlchemy terms
    access_types = Column(
        ARRAY(pgEnum(*[e.value for e in AccessType], name="access_type"))
    )
    data_portal_type: Mapped[Optional[str]]
    record_formats = Column(ARRAY(String))
    update_method: Mapped[Optional[UpdateMethodLiteral]]
    tags = Column(ARRAY(String))
    readme_url: Mapped[Optional[str]]
    originating_entity: Mapped[Optional[str]]
    retention_schedule: Mapped[Optional[RetentionScheduleLiteral]]
    scraper_url: Mapped[Optional[str]]
    submission_notes: Mapped[Optional[str]]
    rejection_note: Mapped[Optional[str]]
    last_approval_editor: Mapped[Optional[int]]
    submitter_contact_info: Mapped[Optional[str]]
    agency_described_not_in_database: Mapped[Optional[str]]
    data_portal_type_other: Mapped[Optional[str]]
    data_source_request: Mapped[Optional[str]]
    broken_source_url_as_of: Mapped[Optional[date]]
    access_notes: Mapped[Optional[text]]
    url_status: Mapped[URLStatusLiteral] = Column(
        Enum(*get_args(URLStatusLiteral), name="url_status"), server_default="ok"
    )
    approval_status: Mapped[ApprovalStatusLiteral]
    record_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("public.record_types.id")
    )
    approval_status_updated_at: Mapped[Optional[timestamp_tz]]

    # Relationships
    locations: Mapped[list[Location]] = relationship(
        argument="Location",
        secondary="public.link_locations_data_sources_view",
        primaryjoin="LinkLocationDataSourceView.data_source_id == DataSource.id",
        secondaryjoin="LinkLocationDataSourceView.location_id == Location.id",
        back_populates="data_sources",
        viewonly=True,
    )
