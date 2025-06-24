# pyright: reportUninitializedInstanceVariable=false
from typing import Optional, get_args

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.helpers import make_get_iter_model_list_of_dict
from db.models.mixins import (
    CountMetadata,
    CountSubqueryMetadata,
    IterWithSpecialCasesMixin,
)
from db.models.templates.standard import StandardBase
from db.models.types import (
    text,
    RequestStatusLiteral,
    timestamp_tz,
    RecordTypeLiteral,
    RequestUrgencyLiteral,
)
from middleware.enums import Relations


class DataRequest(
    StandardBase, CountMetadata, CountSubqueryMetadata, IterWithSpecialCasesMixin
):
    __tablename__ = Relations.DATA_REQUESTS.value

    special_cases = {
        "data_sources": make_get_iter_model_list_of_dict("data_sources"),
        "locations": make_get_iter_model_list_of_dict("locations"),
    }

    submission_notes: Mapped[Optional[str]]
    request_status: Mapped[RequestStatusLiteral] = mapped_column(
        server_default="Intake"
    )
    archive_reason: Mapped[Optional[str]]
    date_created: Mapped[timestamp_tz]
    date_status_last_changed: Mapped[Optional[timestamp_tz]]
    creator_user_id: Mapped[Optional[int]]
    internal_notes: Mapped[Optional[str]]
    record_types_required: Mapped[Optional[ARRAY[RecordTypeLiteral]]] = mapped_column(
        ARRAY(Enum(*get_args(RecordTypeLiteral), name="record_type"), as_tuple=True)
    )
    pdap_response: Mapped[Optional[str]]
    coverage_range: Mapped[Optional[str]]
    data_requirements: Mapped[Optional[str]]
    request_urgency: Mapped[RequestUrgencyLiteral] = mapped_column(
        server_default="Indefinite/Unknown"
    )
    title: Mapped[str]

    # TODO: Is there a way to generalize the below logic?
    locations: Mapped[list["LocationExpanded"]] = relationship(
        argument="LocationExpanded",
        secondary="public.link_locations_data_requests",
        primaryjoin="DataRequest.id == LinkLocationDataRequest.data_request_id",
        secondaryjoin="LocationExpanded.id == LinkLocationDataRequest.location_id",
    )
    github_issue_info = relationship(
        argument="DataRequestsGithubIssueInfo",
        back_populates="data_request",
        uselist=False,
    )
