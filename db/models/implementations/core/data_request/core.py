# pyright: reportUninitializedInstanceVariable=false
from typing import get_args, final

from sqlalchemy import Enum, ForeignKey
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
    RequestStatusLiteral,
    timestamp_tz,
    RecordTypeLiteral,
    RequestUrgencyLiteral,
)
from middleware.enums import Relations


@final
class DataRequest(
    StandardBase, CountMetadata, CountSubqueryMetadata, IterWithSpecialCasesMixin
):
    __tablename__ = Relations.DATA_REQUESTS.value

    special_cases = {
        "data_sources": make_get_iter_model_list_of_dict("data_sources"),
        "locations": make_get_iter_model_list_of_dict("locations"),
    }

    submission_notes: Mapped[str | None]
    request_status: Mapped[RequestStatusLiteral] = mapped_column(
        server_default="Intake"
    )
    archive_reason: Mapped[str | None]
    date_created: Mapped[timestamp_tz]
    date_status_last_changed: Mapped[timestamp_tz | None]
    creator_user_id: Mapped[int | None] = mapped_column(ForeignKey("public.users.id"))  # pyright: ignore [reportUnknownArgumentType]
    internal_notes: Mapped[str | None]
    record_types_required: Mapped[ARRAY[RecordTypeLiteral] | None] = mapped_column(
        ARRAY(Enum(*get_args(RecordTypeLiteral), name="record_type"), as_tuple=True)
    )
    pdap_response: Mapped[str | None]
    coverage_range: Mapped[str | None]
    data_requirements: Mapped[str | None]
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
    data_sources: Mapped[list["DataSource"]] = relationship(
        argument="DataSource",
        secondary="public.link_data_sources_data_requests",
        primaryjoin="DataRequest.id == LinkDataSourceDataRequest.request_id",
        secondaryjoin="DataSource.id == LinkDataSourceDataRequest.data_source_id",
    )
