from collections import namedtuple
from collections.abc import Sequence
from contextlib import contextmanager
from datetime import datetime
from functools import partialmethod
from operator import and_
from typing import (
    Any,
    Callable,
    LiteralString,
    cast,
    final,
)

import psycopg
import sqlalchemy.exc
from psycopg import Cursor
from psycopg.connection import Connection as pg_connection
from psycopg.rows import tuple_row
from sqlalchemy import select, delete, update, Select, func, RowMapping, Executable
from sqlalchemy.orm import (
    selectinload,
    Session,
)
from sqlalchemy.sql.compiler import SQLCompiler

from db.client.decorators import session_manager, session_manager_v2, cursor_manager
from db.client.helpers import initialize_sqlalchemy_session
from db.constants import (
    PAGE_SIZE,
)
from db.db_client_dataclasses import (
    OrderByParameters,
    WhereMapping,
)
from db.dtos.data_request_info_for_github import (
    DataRequestInfoForGithub,
)
from db.dtos.event_batch import EventBatch
from db.dtos.user_with_permissions import UsersWithPermissions
from db.dynamic_query_constructor import DynamicQueryConstructor
from db.enums import (
    ExternalAccountTypeEnum,
    RequestStatus,
    LocationType,
    ApprovalStatus,
    UpdateFrequency,
    UserCapacityEnum,
)
from db.exceptions import LocationDoesNotExistError
from db.helpers_.psycopg import initialize_psycopg_connection
from db.helpers_.result_formatting import (
    get_expanded_display_name,
    agency_to_data_sources_get_related_agencies_output,
)
from db.models.base import Base
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_request.expanded import DataRequestExpanded
from db.models.implementations.core.data_request.github_issue_info import (
    DataRequestsGithubIssueInfo,
)
from db.models.implementations.core.data_source.archive import DataSourceArchiveInfo
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.data_source.expanded import DataSourceExpanded
from db.models.implementations.core.distinct_source_url import DistinctSourceURL
from db.models.implementations.core.external_account import ExternalAccount
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.county import County
from db.models.implementations.core.location.expanded import LocationExpanded
from db.models.implementations.core.log.change import ChangeLog
from db.models.implementations.core.log.notification import NotificationLog
from db.models.implementations.core.log.table_count import TableCountLog
from db.models.implementations.core.notification.queue.data_request import (
    DataRequestUserNotificationQueue,
)
from db.models.implementations.core.notification.queue.data_source import (
    DataSourceUserNotificationQueue,
)
from db.models.implementations.core.permission import Permission
from db.models.implementations.core.record.category import RecordCategory
from db.models.implementations.core.record.type import RecordType
from db.models.implementations.core.reset_token import ResetToken
from db.models.implementations.core.user.core import User
from db.models.implementations.core.user.pending import PendingUser
from db.models.implementations.core.user.permission import UserPermission
from db.models.implementations.link import (
    LinkAgencyLocation,
    LinkUserFollowedLocation,
)
from db.models.table_reference import (
    SQL_ALCHEMY_TABLE_REFERENCE,
)
from db.queries.builder.core import QueryBuilderBase
from db.queries.instantiations.agencies.get_.by_id import GetAgencyByIDQueryBuilder
from db.queries.instantiations.agencies.get_.many import GetAgenciesQueryBuilder
from db.queries.instantiations.data_requests.post import DataRequestsPostQueryBuilder
from db.queries.instantiations.data_requests.put import DataRequestsPutQueryBuilder
from db.queries.instantiations.data_sources.archive import (
    GetDataSourcesToArchiveQueryBuilder,
    ArchiveInfo,
)
from db.queries.instantiations.data_sources.get.by_id import (
    GetDataSourceByIDQueryBuilder,
)
from db.queries.instantiations.data_sources.get.many import (
    GetDataSourcesQueryBuilder,
)
from db.queries.instantiations.data_sources.post.single import (
    DataSourcesPostSingleQueryBuilder,
)
from db.queries.instantiations.data_sources.put import DataSourcesPutQueryBuilder
from db.queries.instantiations.locations.get.many import GetManyLocationsQueryBuilder
from db.queries.instantiations.log.most_recent_logged_table_counts import (
    GetMostRecentLoggedTableCountsQueryBuilder,
)
from db.queries.instantiations.map.counties import GET_MAP_COUNTIES_QUERY
from db.queries.instantiations.map.data_source_count import (
    GET_DATA_SOURCE_COUNT_BY_LOCATION_TYPE_QUERY,
)
from endpoints.instantiations.map.data_sources.query import (
    GET_DATA_SOURCES_FOR_MAP_QUERY,
)
from db.queries.instantiations.map.localities import GET_MAP_LOCALITIES_QUERY
from db.queries.instantiations.map.states import GET_MAP_STATES_QUERY
from db.queries.instantiations.match.agencies import GetSimilarAgenciesQueryBuilder
from db.queries.instantiations.metrics.followed_searches.breakdown import (
    GetMetricsFollowedSearchesBreakdownQueryBuilder,
)
from db.queries.instantiations.metrics.get import GET_METRICS_QUERY
from db.queries.instantiations.notifications.post import NotificationsPostQueryBuilder
from db.queries.instantiations.notifications.preview import (
    NotificationsPreviewQueryBuilder,
)
from db.queries.instantiations.notifications.update_queue import (
    OptionallyUpdateUserNotificationQueueQueryBuilder,
)
from db.queries.instantiations.search.follow.delete import DeleteFollowQueryBuilder
from db.queries.instantiations.search.follow.get import (
    GetUserFollowedSearchesQueryBuilder,
)
from db.queries.instantiations.search.follow.post import CreateFollowQueryBuilder
from db.queries.instantiations.search.record import CreateSearchRecordQueryBuilder
from db.queries.instantiations.source_collector.data_sources import (
    AddDataSourcesFromSourceCollectorQueryBuilder,
)
from db.queries.instantiations.user.create import CreateNewUserQueryBuilder
from db.queries.instantiations.user.get_recent_searches import (
    GetUserRecentSearchesQueryBuilder,
)
from db.queries.instantiations.util.create_entry_in_table import (
    CreateEntryInTableQueryBuilder,
)
from db.queries.instantiations.util.get_columns_for_relation import (
    get_columns_for_relation_query,
)
from db.queries.instantiations.util.refresh_all_materialized_views import (
    REFRESH_ALL_MATERIALIZED_VIEWS_QUERIES,
)
from db.queries.instantiations.util.select_from_relation import (
    SelectFromRelationQueryBuilder,
)
from db.queries.models.get_params import GetParams
from db.subquery_logic import SubqueryParameters
from endpoints.instantiations.auth_.validate_email.query import (
    ValidateEmailQueryBuilder,
)
from endpoints.instantiations.data_requests_.post.dto import DataRequestsPostDTO
from endpoints.instantiations.source_collector.agencies.sync.query import (
    SourceCollectorSyncAgenciesQueryBuilder,
)
from endpoints.instantiations.source_collector.data_sources.post.dtos.request import (
    SourceCollectorPostRequestInnerDTO,
)
from endpoints.instantiations.source_collector.data_sources.post.dtos.response import (
    SourceCollectorPostResponseInnerDTO,
)
from endpoints.instantiations.source_collector.agencies.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)
from endpoints.instantiations.source_collector.data_sources.sync.dtos.request import (
    SourceCollectorSyncDataSourcesRequestDTO,
)
from endpoints.instantiations.source_collector.data_sources.sync.dtos.response import (
    SourceCollectorSyncDataSourcesResponseDTO,
)
from endpoints.instantiations.source_collector.data_sources.sync.query.core import (
    SourceCollectorSyncDataSourcesQueryBuilder,
)
from endpoints.instantiations.user.by_id.get.dto import (
    UserProfileResponseSchemaInnerDTO,
)
from endpoints.instantiations.user.by_id.get.query import GetUserByIdQueryBuilder
from endpoints.instantiations.user.by_id.patch.dto import UserPatchDTO
from endpoints.instantiations.user.by_id.patch.query import UserPatchQueryBuilder
from middleware.constants import DATE_FORMAT
from middleware.enums import (
    PermissionsEnum,
    Relations,
    RecordTypes,
)
from middleware.exceptions import (
    UserNotFoundError,
)
from middleware.miscellaneous.table_count_logic import (
    TableCountReference,
    TableCountReferenceManager,
)
from middleware.schema_and_dto.dtos.agencies.post import AgenciesPostDTO
from middleware.schema_and_dto.dtos.data_requests.put import DataRequestsPutOuterDTO
from middleware.schema_and_dto.dtos.data_sources.post import DataSourcesPostDTO
from middleware.schema_and_dto.dtos.entry_create_update_request import (
    EntryCreateUpdateRequestDTO,
)
from middleware.schema_and_dto.dtos.locations.put import LocationPutDTO
from middleware.schema_and_dto.dtos.match.response import (
    AgencyMatchResponseInnerDTO,
)
from middleware.schema_and_dto.dtos.metrics import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)
from middleware.schema_and_dto.dtos.notifications.preview import (
    NotificationsPreviewOutput,
)
from middleware.util.argument_checking import check_for_mutually_exclusive_arguments
from utilities.enums import RecordCategoryEnum


@final
class DatabaseClient:
    def __init__(self):
        self.connection: pg_connection = initialize_psycopg_connection()
        self.session_maker = initialize_sqlalchemy_session()
        self.session: Session | None = None
        self.cursor: Cursor | None = None

    @cursor_manager()
    def execute_raw_sql(
        self, query: str, vars_: tuple | None = None, execute_many: bool = False
    ) -> list[dict[Any, ...]] | None:
        """Executes an SQL query passed to the function.

        :param query: The SQL query to execute.
        :param vars_: A tuple of variables to replace placeholders in the SQL query, defaults to None
        :param execute_many: Whether to execute the query with executemany, defaults to False
        :return: A list of dicts, or None if there are no results.
        """
        if execute_many:
            self.cursor.executemany(cast(LiteralString, query), vars_)
        else:
            _ = self.cursor.execute(cast(LiteralString, query), vars_)
        try:
            results = self.cursor.fetchall()
        except psycopg.ProgrammingError:
            return None

        if len(results) == 0:
            return None
        return results

    @staticmethod
    def compile(query: Select) -> SQLCompiler:
        return query.compile(compile_kwargs={"literal_binds": True})

    @session_manager_v2
    def scalar(self, session: Session, query: Select):
        return session.execute(query).scalar()

    @session_manager_v2
    def scalars(self, session: Session, query: Select):
        return session.execute(query).scalars().all()

    @session_manager_v2
    def one(self, session: Session, query: Select):
        return session.execute(query).one()

    @session_manager_v2
    def execute_sqlalchemy(self, session: Session, query: Callable):
        results = session.execute(query())
        return results

    @session_manager_v2
    def all(self, session: Session, stmt: Executable):
        return session.execute(stmt).all()

    @session_manager_v2
    def execute(self, session: Session, stmt: Executable):
        session.execute(stmt)

    @session_manager_v2
    def add(self, session: Session, model: Base):
        session.add(model)

    @session_manager_v2
    def add_many(
        self, session: Session, models: list[Base], return_ids: bool = False
    ) -> list[int] | None:
        session.add_all(models)
        if return_ids:
            if not hasattr(models[0], "id"):
                raise AttributeError("Models must have an id attribute")
            session.flush()
            return [
                model.id  # pyright: ignore [reportAttributeAccessIssue]
                for model in models
            ]
        return None

    @session_manager_v2
    def mapping(self, session: Session, query: Executable) -> RowMapping | None:
        return session.execute(query).mappings().first()

    @session_manager_v2
    def mappings(self, session: Session, query: Executable) -> Sequence[RowMapping]:
        return session.execute(query).mappings().all()

    @contextmanager
    def session_scope(self):
        session: Session = self.session_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_new_user(
        self,
        email: str,
        password_digest: str,
        capacities: list[UserCapacityEnum] | None = None,
    ) -> int | None:
        """Adds a new user to the database."""
        builder = CreateNewUserQueryBuilder(
            email=email, password_digest=password_digest, capacities=capacities
        )
        return self.run_query_builder(builder)

    def get_user_id(self, email: str) -> int | None:
        """Gets the ID of a user in the database based on their email."""
        query = select(User.id).where(User.email == email)
        return self.scalar(query)

    def update_user_password_digest(self, user_id: int, password_digest: str):
        """Update user's password digest."""
        query = (
            update(User)
            .where(User.id == user_id)
            .values(password_digest=password_digest)
        )
        self.execute(query)

    def get_password_digest(self, user_id: int) -> str:
        query = select(User.password_digest).where(User.id == user_id)
        return self.scalar(query)

    def password_digest_matches(self, user_id: int, password_digest: str) -> bool:
        return password_digest == self.get_password_digest(user_id)

    ResetTokenInfo = namedtuple("ResetTokenInfo", ["id", "user_id", "create_date"])

    def get_reset_token_info(self, token: str) -> ResetTokenInfo | None:
        """
        Check if reset token exists in the database and retrieves the associated user data.

        :param token: The reset token to check.
        :return: ResetTokenInfo if the token exists; otherwise, None.
        """
        rt = ResetToken
        query = select(rt.id, rt.user_id, rt.create_date).where(rt.token == token)
        result = self.mapping(query)
        if result is None:
            return None
        return self.ResetTokenInfo(
            id=result["id"],
            user_id=result["user_id"],
            create_date=result["create_date"],
        )

    def add_reset_token(self, user_id: int, token: str):
        """Inserts a new reset token into the database for a specified user."""
        self.add(ResetToken(user_id=user_id, token=token))

    def delete_reset_token(self, user_id: int, token: str):
        """Deletes a reset token from the database for a specified user id."""
        query = delete(ResetToken).where(
            ResetToken.user_id == user_id, ResetToken.token == token
        )
        self.execute(query)

    UserIdentifiers = namedtuple("UserIdentifiers", ["id", "email"])

    def get_user_by_api_key(self, api_key: str) -> UserIdentifiers | None:
        """
        Get user id for a given api key
        :return: RoleInfo if the token exists; otherwise, None.
        """
        query = select(User.id, User.email).where(User.api_key == api_key)
        result = self.mapping(query)
        if result is None:
            return None
        return self.UserIdentifiers(id=result["id"], email=result["email"])

    def get_user_profile(self, user_id: int) -> UserProfileResponseSchemaInnerDTO:
        builder = GetUserByIdQueryBuilder(user_id)
        return self.run_query_builder(builder)

    def update_user_api_key(self, api_key: str, user_id: int):
        """Update the api key for a user."""
        query = update(User).where(User.id == user_id).values(api_key=api_key)
        self.execute(query)

    MapInfo = namedtuple(
        "MapInfo",
        [
            "data_source_id",
            "location_id",
            "data_source_name",
            "agency_id",
            "agency_name",
            "state",
            "municipality",
            "county",
            "record_type",
            "lat",
            "lng",
        ],
    )

    @cursor_manager(row_factory=tuple_row)
    def get_data_sources_for_map(self) -> list[MapInfo]:
        """Return a list of data sources with relevant info for the map."""
        self.cursor.execute(cast(LiteralString, GET_DATA_SOURCES_FOR_MAP_QUERY))
        results = self.cursor.fetchall()

        return [self.MapInfo(*result) for result in results]

    def get_data_sources_to_archive(
        self,
        update_frequency: UpdateFrequency | None = None,
        last_archived_before: datetime | None = None,
        page: int = 1,
    ) -> list[ArchiveInfo]:
        """Pulls data sources to be archived by the automatic archives script."""
        builder = GetDataSourcesToArchiveQueryBuilder(
            update_frequency=update_frequency,
            last_archived_before=last_archived_before,
            page=page,
        )
        return self.run_query_builder(builder)

    def update_url_status_to_broken(
        self, data_source_id: str, broken_as_of: str
    ) -> None:
        """
        Update a data sources' url_status to 'broken'.

        :param data_source_id: The id of the data source.
        :param broken_as_of: The date when the source was identified as broken.
        """
        query = (
            update(DataSource)
            .where(DataSource.id == data_source_id)
            .values(url_status="broken", broken_source_url_as_of=broken_as_of)
        )
        self.execute(query)

    def update_last_cached(self, data_source_id: str, last_cached: str) -> None:
        """Update when a data source was last cached."""
        d = DataSourceArchiveInfo
        query = (
            update(d)
            .where(d.data_source_id == data_source_id)
            .values(last_cached=last_cached)
        )
        self.execute(query)

    DataSourceMatches = namedtuple("DataSourceMatches", ["converted", "ids"])

    UserInfo = namedtuple("UserInfo", ["id", "password_digest", "api_key", "email"])

    def get_user_info(self, user_email: str) -> UserInfo:
        """
        Retrieves user data by email.

        :param user_email: User's email.
        :raise UserNotFoundError: If no user is found.
        :return: UserInfo namedtuple containing the user's information.
        """
        query = select(
            User.id,
            User.password_digest,
            User.api_key,
            User.email,
        ).where(User.email == user_email)
        result = self.mapping(query)
        if result is None:
            raise UserNotFoundError(user_email)

        return self.UserInfo(
            id=result["id"],
            password_digest=result["password_digest"],
            api_key=result["api_key"],
            email=result["email"],
        )

    def get_user_info_by_external_account_id(
        self, external_account_id: str, external_account_type: ExternalAccountTypeEnum
    ) -> UserInfo:
        u = User
        ea = ExternalAccount

        query = (
            select(u.id, u.email, u.password_digest, u.api_key)
            .join(ea, u.id == ea.user_id)
            .where(
                ea.account_identifier == external_account_id,
                ea.account_type == external_account_type.value,
            )
        )
        results = self.mapping(query)

        if results is None:
            raise UserNotFoundError(
                identifier=external_account_id, identifier_name="Github Account ID"
            )

        return self.UserInfo(
            id=results.id,
            password_digest=results.password_digest,
            api_key=results.api_key,
            email=results.email,
        )

    @cursor_manager()
    def get_typeahead_locations(self, search_term: str) -> list[dict]:
        """Return a list of data sources that match the search query."""
        query = DynamicQueryConstructor.generate_like_typeahead_locations_query(
            search_term
        )
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        if 0 < len(results) <= 10:
            return results

        fuzzy_match_query = (
            DynamicQueryConstructor.generate_fuzzy_match_typeahead_locations_query(
                search_term
            )
        )
        self.cursor.execute(fuzzy_match_query)
        return self.cursor.fetchall()

    @cursor_manager()
    def get_typeahead_agencies(self, search_term: str) -> list[dict]:
        """Return a list of data sources that match the search query."""
        query = DynamicQueryConstructor.generate_new_typeahead_agencies_query(
            search_term
        )
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @cursor_manager()
    def search_with_location_and_record_type(
        self,
        location_id: int,
        record_categories: list[RecordCategoryEnum] | None = None,
        record_types: list[RecordTypes] | None = None,
    ) -> list[dict]:
        """Search for data sources in the database."""
        check_for_mutually_exclusive_arguments(record_categories, record_types)

        query = DynamicQueryConstructor.create_search_query(
            location_id=location_id,
            record_categories=record_categories,
            record_types=record_types,
        )
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @cursor_manager()
    def search_federal_records(
        self, record_categories: list[RecordCategoryEnum] | None = None, page: int = 1
    ) -> list[dict]:
        query = DynamicQueryConstructor.create_federal_search_query(
            page=page,
            record_categories=record_categories,
        )
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def link_external_account(
        self,
        user_id: str,
        external_account_id: str,
        external_account_type: ExternalAccountTypeEnum,
    ):
        """Links an external account to a user."""
        ea = ExternalAccount(
            user_id=int(user_id),
            account_type=external_account_type.value,
            account_identifier=external_account_id,
        )
        self.add(ea)

    @session_manager
    def get_table_count(self, table_name: str) -> int:
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        if not hasattr(table, "id"):
            raise ValueError(f"Table {table_name} does not have an id column")
        count = self.session.query(
            func.count(table.id)  # pyright: ignore[reportAttributeAccessIssue]
        ).scalar()
        return count

    @session_manager
    def log_table_counts(self, tcrs: list[TableCountReference]):
        # Add entry to TableCountLog
        for tcr in tcrs:
            new_entry = TableCountLog(table_name=tcr.table, count=tcr.count)
            self.session.add(new_entry)

    @session_manager
    def get_most_recent_logged_table_counts(self) -> TableCountReferenceManager:
        """Get the most recent table count for all distinct tables"""
        return self.run_query_builder(GetMostRecentLoggedTableCountsQueryBuilder())

    def add_user_permission(self, user_id: str or int, permission: PermissionsEnum):
        """Add a permission to a user."""
        permission_id_subquery = (
            select(Permission.id)
            .where(Permission.permission_name == permission.value)
            .scalar_subquery()
        )
        up = UserPermission(
            user_id=user_id,
            permission_id=cast(int, permission_id_subquery),  # pyright: ignore[reportInvalidCast]
        )
        self.add(up)

    def remove_user_permission(self, user_id: str, permission: PermissionsEnum):
        query = delete(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_id
            == (
                select(Permission.id).where(
                    Permission.permission_name == permission.value
                )
            ),
        )
        self.execute(query)

    def get_user_permissions(self, user_id: int) -> list[PermissionsEnum]:
        query = (
            select(Permission.permission_name)
            .select_from(UserPermission)
            .join(Permission, UserPermission.permission_id == Permission.id)
            .where(UserPermission.user_id == user_id)
        )
        results = self.mappings(query)
        return [PermissionsEnum(row["permission_name"]) for row in results]

    @session_manager_v2
    def _update_entry_in_table(
        self,
        session: Session,
        table_name: str,
        entry_id: Any,
        column_edit_mappings: dict[str, Any],
        id_column_name: str = "id",
    ):
        """
        Updates a specific entry in a table in the database.

        :param table_name: The name of the table to update.
        :param entry_id: The ID of the entry to update.
        :param column_edit_mappings: A dictionary mapping column names to their new values.
        """
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        query_base = update(table)
        column = getattr(table, id_column_name)
        query_where = query_base.where(column == entry_id)
        query_values = query_where.values(**column_edit_mappings)
        session.execute(query_values)

    update_data_source = partialmethod(
        _update_entry_in_table, table_name="data_sources", id_column_name="id"
    )

    def update_data_source_v2(
        self,
        dto: EntryCreateUpdateRequestDTO,
        data_source_id: int,
        permissions: list[PermissionsEnum],
        user_id: int,
    ) -> None:
        builder = DataSourcesPutQueryBuilder(
            dto=dto,
            data_source_id=data_source_id,
            permissions=permissions,
            user_id=user_id,
        )
        self.run_query_builder(builder)

    update_data_request = partialmethod(
        _update_entry_in_table,
        table_name="data_requests",
    )

    def update_data_request_v2(
        self,
        dto: DataRequestsPutOuterDTO,
        data_request_id: int,
        user_id: int | None = None,
        permissions: list[PermissionsEnum] | None = None,
        bypass_permissions: bool = False,
    ) -> None:
        builder = DataRequestsPutQueryBuilder(
            dto=dto,
            data_request_id=data_request_id,
            user_id=user_id,
            permissions=permissions,
            bypass_permissions=bypass_permissions,
        )
        self.run_query_builder(builder)

    update_agency = partialmethod(
        _update_entry_in_table,
        table_name="agencies",
        id_column_name="id",
    )

    def _create_entry_in_table(
        self,
        table_name: str,
        column_value_mappings: dict[str, str],
        column_to_return: str | None = None,
    ) -> Any | None:
        builder = CreateEntryInTableQueryBuilder(
            table_name=table_name,
            column_value_mappings=column_value_mappings,
            column_to_return=column_to_return,
        )
        return self.run_query_builder(builder)

    create_data_request = partialmethod(
        _create_entry_in_table, table_name="data_requests", column_to_return="id"
    )

    def create_data_request_v2(
        self,
        dto: DataRequestsPostDTO,
        user_id: int,
    ) -> int:
        builder = DataRequestsPostQueryBuilder(
            dto=dto,
            user_id=user_id,
        )
        return self.run_query_builder(builder)

    @session_manager_v2
    def create_agency(
        self,
        session: Session,
        dto: AgenciesPostDTO,
        user_id: int | None = None,
    ):
        # Create Agency Entry
        agency_info = dto.agency_info
        agency = Agency(
            name=agency_info.name,
            agency_type=agency_info.agency_type.value,
            jurisdiction_type=agency_info.jurisdiction_type.value,
            multi_agency=agency_info.multi_agency,
            no_web_presence=agency_info.no_web_presence,
            approval_status=agency_info.approval_status.value,
            homepage_url=agency_info.homepage_url,
            defunct_year=agency_info.defunct_year,
            rejection_reason=agency_info.rejection_reason,
            last_approval_editor=agency_info.last_approval_editor,
            submitter_contact=agency_info.submitter_contact,
            creator_user_id=user_id,
        )
        session.add(agency)

        # Flush to get agency id
        session.flush()

        # Link to Locations
        if dto.location_ids is not None:
            for location_id in dto.location_ids:
                lal = LinkAgencyLocation(location_id=location_id, agency_id=agency.id)
                session.add(lal)

        return agency.id

    def add_location_to_agency(self, location_id: int, agency_id: int):
        self.add(LinkAgencyLocation(location_id=location_id, agency_id=agency_id))

    def remove_location_from_agency(self, location_id: int, agency_id: int):
        query = delete(LinkAgencyLocation).where(
            and_(
                LinkAgencyLocation.location_id == location_id,
                LinkAgencyLocation.agency_id == agency_id,
            )
        )
        self.execute(query)

    create_request_source_relation = partialmethod(
        _create_entry_in_table,
        table_name=Relations.LINK_DATA_SOURCES_DATA_REQUESTS.value,
        column_to_return="id",
    )

    create_data_source_agency_relation = partialmethod(
        _create_entry_in_table,
        table_name=Relations.LINK_AGENCIES_DATA_SOURCES.value,
        column_to_return="id",
    )

    create_request_location_relation = partialmethod(
        _create_entry_in_table,
        table_name=Relations.LINK_LOCATIONS_DATA_REQUESTS.value,
        column_to_return="id",
    )

    def add_data_source_v2(self, dto: DataSourcesPostDTO) -> int:
        builder = DataSourcesPostSingleQueryBuilder(dto)
        return self.run_query_builder(builder)

    create_data_request_github_info = partialmethod(
        _create_entry_in_table,
        table_name=Relations.DATA_REQUESTS_GITHUB_ISSUE_INFO.value,
    )

    create_locality = partialmethod(
        _create_entry_in_table,
        table_name=Relations.LOCALITIES.value,
        column_to_return="id",
    )

    def create_followed_search(
        self,
        user_id: int,
        location_id: int,
        record_types: list[RecordTypes] | None = None,
        record_categories: list[RecordCategoryEnum] | None = None,
    ) -> None:
        builder = CreateFollowQueryBuilder(
            user_id=user_id,
            location_id=location_id,
            record_types=record_types,
            record_categories=record_categories,
        )
        return self.run_query_builder(builder)

    def create_county(self, name: str, fips: str, state_id: int) -> int:
        """Create county and return county id."""
        return self._create_entry_in_table(
            table_name=Relations.COUNTIES.value,
            column_value_mappings={"name": name, "fips": fips, "state_id": state_id},
            column_to_return="id",
        )

    def _select_from_relation(
        self,
        relation_name: str,
        columns: list[str],
        where_mappings: list[WhereMapping] | dict | None = [True],
        limit: int | None = PAGE_SIZE,
        page: int | None = None,
        order_by: OrderByParameters | None = None,
        subquery_parameters: list[SubqueryParameters] | None = [],
        build_metadata: bool | None = False,
        alias_mappings: dict[str, str] | None = None,
        apply_uniqueness_constraints: bool | None = True,
    ) -> list[dict]:
        builder = SelectFromRelationQueryBuilder(
            relation_name=relation_name,
            columns=columns,
            where_mappings=where_mappings,
            limit=limit,
            page=page,
            order_by=order_by,
            subquery_parameters=subquery_parameters,
            build_metadata=build_metadata,
            alias_mappings=alias_mappings,
            apply_uniqueness_constraints=apply_uniqueness_constraints,
        )
        return self.run_query_builder(builder)

    get_data_requests = partialmethod(
        _select_from_relation, relation_name=Relations.DATA_REQUESTS_EXPANDED.value
    )

    @session_manager
    def get_data_requests_ready_to_start_without_github_issue(
        self,
    ) -> list[DataRequestInfoForGithub]:
        query = (
            select(DataRequest)
            .where(
                and_(
                    DataRequest.request_status == RequestStatus.READY_TO_START.value,
                    DataRequestsGithubIssueInfo.id.is_(None),
                )
            )
            .outerjoin(DataRequestsGithubIssueInfo)
            .options(selectinload(DataRequest.locations))
        )

        execute_results = self.session.execute(query).scalars()

        raw_results = execute_results.all()

        final_results = []
        for result in raw_results:
            display_names = []
            for location in result.locations:
                display_names.append(location.display_name)
            dto = DataRequestInfoForGithub(
                id=result.id,
                title=result.title,
                submission_notes=result.submission_notes,
                data_requirements=result.data_requirements,
                locations=display_names,
                record_types=result.record_types_required,
            )
            final_results.append(dto)

        return final_results

    def get_agencies(
        self,
        order_by: OrderByParameters | None = None,
        page: int | None = 1,
        limit: int | None = PAGE_SIZE,
        requested_columns: list[str] | None = None,
        approval_status: ApprovalStatus | None = None,
    ):
        params = GetParams(
            order_by=order_by,
            page=page,
            limit=limit,
            requested_columns=requested_columns,
        )
        builder = GetAgenciesQueryBuilder(
            params=params,
            approval_status=approval_status,
        )
        return self.run_query_builder(builder)

    def get_agency_by_id(
        self,
        agency_id: int,
    ):
        builder = GetAgencyByIDQueryBuilder(agency_id)
        return self.run_query_builder(builder)

    def get_data_sources(
        self,
        data_sources_columns: list[str],
        data_requests_columns: list[str],
        order_by: OrderByParameters | None = None,
        page: int | None = 1,
        limit: int | None = PAGE_SIZE,
        approval_status: ApprovalStatus | None = None,
    ):
        builder = GetDataSourcesQueryBuilder(
            data_sources_columns=data_sources_columns,
            data_requests_columns=data_requests_columns,
            order_by=order_by,
            page=page,
            limit=limit,
            approval_status=approval_status,
        )
        return self.run_query_builder(builder)

    @session_manager_v2
    def get_data_source_related_agencies(
        self,
        session: Session,
        data_source_id: int,
    ) -> list[dict] | None:
        query = (
            select(DataSourceExpanded)
            .options(
                selectinload(DataSourceExpanded.agencies).selectinload(Agency.locations)
            )
            .where(DataSourceExpanded.id == data_source_id)
        )

        result: DataSourceExpanded = (
            session.execute(query).scalars(DataSourceExpanded).first()
        )
        if result is None:
            return None

        agency_dicts = []
        for agency in result.agencies:
            agency_dict = agency_to_data_sources_get_related_agencies_output(agency)
            agency_dicts.append(agency_dict)

        return agency_dicts

    def get_data_source_by_id(
        self,
        data_source_id: int,
        data_sources_columns: list[str],
        data_requests_columns: list[str],
    ):
        builder = GetDataSourceByIDQueryBuilder(
            data_source_id=data_source_id,
            data_sources_columns=data_sources_columns,
            data_requests_columns=data_requests_columns,
        )
        return self.run_query_builder(builder)

    @session_manager_v2
    def run_query_builder(
        self, session: Session, query_builder: QueryBuilderBase
    ) -> Any:
        return query_builder.build(session)

    def _select_single_entry_from_relation(
        self,
        relation_name: str,
        columns: list[str],
        where_mappings: list[WhereMapping] | dict | None = [True],
        subquery_parameters: list[SubqueryParameters] | None = [],
        **kwargs,
    ) -> Any:
        results = self._select_from_relation(
            relation_name=relation_name,
            columns=columns,
            where_mappings=where_mappings,
            subquery_parameters=subquery_parameters,
            **kwargs,
        )
        if len(results) == 0:
            return None
        if len(results) > 1:
            raise RuntimeError(f"Expected 1 result but found {len(results)}")
        return results[0]

    def get_location_id(self, where_mappings: list[WhereMapping] | dict) -> int | None:
        result = self._select_single_entry_from_relation(
            relation_name=Relations.LOCATIONS_EXPANDED.value,
            columns=["id"],
            where_mappings=where_mappings,
        )
        if result is None:
            return None
        return result["id"]

    def get_data_requests_for_creator(
        self, creator_user_id: str, columns: list[str]
    ) -> Sequence[RowMapping]:
        selects = []
        for column in columns:
            sel = getattr(DataRequest, column)
            selects.append(sel)
        query = select(*selects).where(DataRequest.creator_user_id == creator_user_id)
        return self.mappings(query)

    def user_is_creator_of_data_request(
        self, user_id: int, data_request_id: int
    ) -> bool:
        query = select(DataRequest.id).where(
            DataRequest.creator_user_id == int(user_id),
            DataRequest.id == int(data_request_id),
        )
        result = self.scalar(query)
        return result is not None

    @session_manager_v2
    def _delete_from_table(
        self,
        session: Session,
        table_name: str,
        id_column_value: str | int,
        id_column_name: str = "id",
    ):
        """Delete an entry from a table in the database."""
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        column = getattr(table, id_column_name)
        query = delete(table).where(column == id_column_value)
        session.execute(query)

    delete_data_request = partialmethod(_delete_from_table, table_name="data_requests")

    delete_agency = partialmethod(_delete_from_table, table_name="agencies")

    delete_data_source = partialmethod(_delete_from_table, table_name="data_sources")

    delete_request_source_relation = partialmethod(
        _delete_from_table, table_name=Relations.RELATED_SOURCES.value
    )

    delete_request_location_relation = partialmethod(
        _delete_from_table, table_name=Relations.LINK_LOCATIONS_DATA_REQUESTS.value
    )

    def delete_followed_search(
        self,
        user_id: int,
        location_id: int,
        record_types: list[RecordTypes] | None = None,
        record_categories: list[RecordCategoryEnum] | None = None,
    ):
        builder = DeleteFollowQueryBuilder(
            user_id=user_id,
            location_id=location_id,
            record_types=record_types,
            record_categories=record_categories,
        )
        return self.run_query_builder(builder)

    delete_data_source_agency_relation = partialmethod(
        _delete_from_table, table_name=Relations.LINK_AGENCIES_DATA_SOURCES.value
    )

    @cursor_manager()
    def check_for_url_duplicates(self, url: str) -> list[dict]:
        query = DynamicQueryConstructor.get_distinct_source_urls_query(url)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_columns_for_relation(self, relation: Relations) -> list[dict]:
        """Get columns for a given relation."""
        results = self.execute_raw_sql(get_columns_for_relation_query(relation))
        return [row["column_name"] for row in results]

    def get_county_id(self, county_name: str, state_id: int) -> int:
        query = select(County.id).where(
            County.name == county_name,
            County.state_id == state_id,
        )
        return self.scalar(query)

    def create_or_get(
        self,
        table_name: str,
        column_value_mappings: dict[str, str],
        column_to_return: str = "id",
    ):
        """Create a value and return the id if it doesn't exist; if it does, return the id for it."""
        try:
            return self._create_entry_in_table(
                table_name=table_name,
                column_value_mappings=column_value_mappings,
                column_to_return=column_to_return,
            )
        except sqlalchemy.exc.IntegrityError:
            return self._select_from_relation(
                relation_name=table_name,
                columns=[column_to_return],
                where_mappings=WhereMapping.from_dict(column_value_mappings),
            )[0][column_to_return]

    def get_linked_rows(
        self,
        link_table: Relations,
        left_id: str,
        left_link_column: str,
        right_link_column: str,
        linked_relation: Relations,
        linked_relation_linking_column: str,
        columns_to_retrieve: list[str],
        alias_mappings: dict[str, str] | None = None,
        build_metadata=False,
        subquery_parameters: list[SubqueryParameters] | None = [],
    ):
        # Get ids via linked table
        link_results = self._select_from_relation(
            relation_name=link_table.value,
            columns=[right_link_column],
            where_mappings={left_link_column: left_id},
        )
        link_ids = [result[right_link_column] for result in link_results]
        linked_results = self._select_from_relation(
            relation_name=linked_relation.value,
            columns=columns_to_retrieve,
            alias_mappings=alias_mappings,
            where_mappings={linked_relation_linking_column: link_ids},
            build_metadata=build_metadata,
            subquery_parameters=subquery_parameters,
        )
        return linked_results

    def get_user_followed_searches(self, user_id: int) -> dict[str, Any]:
        return self.run_query_builder(
            GetUserFollowedSearchesQueryBuilder(user_id=user_id)
        )

    DataRequestIssueInfo = namedtuple(
        "DataRequestIssueInfo",
        [
            "data_request_id",
            "github_issue_url",
            "github_issue_number",
            "request_status",
            "record_types_required",
        ],
    )

    def get_unarchived_data_requests_with_issues(self) -> list[DataRequestIssueInfo]:
        dre = DataRequestExpanded
        query = select(
            dre.id,
            dre.github_issue_url,
            dre.github_issue_number,
            dre.request_status,
            dre.record_types_required,
        ).where(
            dre.request_status != RequestStatus.ARCHIVED.value,
            dre.github_issue_url.isnot(None),
        )

        results = self.mappings(query)

        return [
            self.DataRequestIssueInfo(
                data_request_id=result["id"],
                github_issue_url=result["github_issue_url"],
                github_issue_number=result["github_issue_number"],
                request_status=RequestStatus(result["request_status"]),
                record_types_required=result["record_types_required"],
            )
            for result in results
        ]

    def optionally_update_user_notification_queue(self) -> None:
        return self.run_query_builder(
            OptionallyUpdateUserNotificationQueueQueryBuilder()
        )

    def get_national_location_id(self) -> int:
        query = select(Location.id).where(
            Location.state_id.is_(None),
            Location.county_id.is_(None),
            Location.locality_id.is_(None),
        )
        return self.scalar(query)

    def get_next_user_event_batch(self) -> EventBatch | None:
        return self.run_query_builder(NotificationsPostQueryBuilder())

    def preview_notifications(self) -> NotificationsPreviewOutput:
        return self.run_query_builder(NotificationsPreviewQueryBuilder())

    @session_manager
    def mark_user_events_as_sent(self, user_id: int):
        with self.session.begin():
            for queue in (
                DataRequestUserNotificationQueue,
                DataSourceUserNotificationQueue,
            ):
                self.session.query(queue).filter(queue.user_id == user_id).update(
                    {queue.sent_at: datetime.now()}
                )

    def create_search_record(
        self,
        user_id: int,
        location_id: int,
        record_categories: list[RecordCategoryEnum] | RecordCategoryEnum | None = None,
        record_types: list[RecordTypes] | RecordTypes | None = None,
    ):
        builder = CreateSearchRecordQueryBuilder(
            user_id=user_id,
            location_id=location_id,
            record_categories=record_categories,
            record_types=record_types,
        )
        return self.run_query_builder(builder)

    def get_user_recent_searches(self, user_id: int):
        return self.run_query_builder(GetUserRecentSearchesQueryBuilder(user_id))

    def get_record_type_id_by_name(self, record_type_name: str):
        query = select(RecordType.id).where(RecordType.name == record_type_name)
        return self.scalar(query)

    def get_user_external_accounts(self, user_id: int):
        ea = ExternalAccount
        query = select(ea.account_type, ea.account_identifier).where(
            ea.user_id == user_id
        )
        raw_results = self.mappings(query)
        return {row["account_type"]: row["account_identifier"] for row in raw_results}

    def get_change_logs_for_table(self, table: Relations):
        query = select(
            ChangeLog.id,
            ChangeLog.operation_type,
            ChangeLog.table_name,
            ChangeLog.affected_id,
            ChangeLog.old_data,
            ChangeLog.new_data,
            ChangeLog.created_at,
        ).where(ChangeLog.table_name == table.value)
        return self.mappings(query)

    @session_manager
    def get_users(self, page: int) -> list[UsersWithPermissions]:
        # TODO: QueryBuilder
        raw_results = self.session.execute(
            select(User)
            .options(selectinload(User.permissions))
            .order_by(User.created_at.desc())
            .limit(100)
            .offset((page - 1) * 100)
        ).all()

        final_results = []

        for raw_result in raw_results:
            user = raw_result[0]
            permissions_db = user.permissions
            permissions_str = [
                permission.permission_name for permission in permissions_db
            ]
            permissions_enum = [
                PermissionsEnum(permission) for permission in permissions_str
            ]
            uwp = UsersWithPermissions(
                user_id=user.id,
                email=user.email,
                created_at=user.created_at,
                updated_at=user.updated_at,
                permissions=permissions_enum,
            )
            final_results.append(uwp)

        return final_results

    def get_user_email(self, user_id: int) -> str:
        query = select(User.email).where(User.id == user_id)
        return self.scalar(query)

    def pending_user_exists(self, email: str) -> bool:
        query = select(PendingUser.id).where(PendingUser.email == email)
        result = self.scalar(query)
        return result is not None

    def create_pending_user(
        self,
        email: str,
        password_digest: str,
        validation_token: str,
        capacities: list[UserCapacityEnum] | None,
    ):
        self.add(
            PendingUser(
                email=email,
                password_digest=password_digest,
                validation_token=validation_token,
                capacities=[capacity.value for capacity in capacities]
                if capacities
                else [],
            )
        )

    def delete_user(self, user_id: int):
        query = delete(User).where(User.id == user_id)
        self.execute(query)

    def update_pending_user_validation_token(self, email: str, validation_token: str):
        query = (
            update(PendingUser)
            .where(PendingUser.email == email)
            .values(validation_token=validation_token)
        )
        self.execute(query)

    def get_locality_id_by_location_id(self, location_id: int):
        query = select(Location.locality_id).where(Location.id == location_id)
        return self.scalar(query)

    @session_manager
    def get_location_by_id(self, location_id: int):
        query = Select(
            LocationExpanded,
        ).where(LocationExpanded.id == location_id)

        result = self.session.execute(query).scalar()

        if result is None:
            raise ValueError(f"Location with id {location_id} not found")

        return {
            "type": result.type,
            "location_id": result.id,
            "state_name": result.state_name,
            "state_iso": result.state_iso,
            "county_name": result.county_name,
            "county_fips": result.county_fips,
            "locality_name": result.locality_name,
            "display_name": get_expanded_display_name(result),
        }

    def get_similar_agencies(
        self,
        name: str,
        location_id: int | None = None,
    ) -> list[AgencyMatchResponseInnerDTO]:
        builder = GetSimilarAgenciesQueryBuilder(name=name, location_id=location_id)
        return self.run_query_builder(builder)

    def get_metrics(self):
        result = self.execute_raw_sql(GET_METRICS_QUERY)
        d = {}
        for row in result:
            d[row["Count Type"]] = row["count"]
        return d

    @session_manager
    def get_record_types_and_categories(self):
        query = (
            select(RecordCategory)
            .options(selectinload(RecordCategory.record_types))
            .order_by(RecordCategory.id)
        )

        results: list[RecordCategory] = self.session.execute(query).scalars().all()

        record_types = []
        record_categories = []
        for result in results:
            record_cat_dict = {
                "id": result.id,
                "name": result.name,
                "description": result.description,
            }
            record_categories.append(record_cat_dict)
            for record_type in result.record_types:
                record_type_dict = {
                    "id": record_type.id,
                    "name": record_type.name,
                    "category_id": record_type.category_id,
                    "description": record_type.description,
                }
                record_types.append(record_type_dict)

        return {"record_types": record_types, "record_categories": record_categories}

    def reject_data_source(self, data_source_id: int, rejection_note: str):
        self.update_data_source(
            entry_id=data_source_id,
            column_edit_mappings={
                "approval_status": ApprovalStatus.REJECTED.value,
                "rejection_note": rejection_note,
            },
        )

    @session_manager
    def get_all(self, model: type[Base]):
        def to_dict(instance):
            return {
                c.name: getattr(instance, c.name) for c in instance.__table__.columns
            }

        results = self.session.query(model).all()

        return [to_dict(result) for result in results]

    def add_data_sources_from_source_collector(
        self, data_sources: list[SourceCollectorPostRequestInnerDTO]
    ) -> list[SourceCollectorPostResponseInnerDTO]:
        builder = AddDataSourcesFromSourceCollectorQueryBuilder(data_sources)
        return self.run_query_builder(builder)

    @session_manager
    def update_location_by_id(self, location_id: int, dto: LocationPutDTO):
        if dto.latitude is None or dto.longitude is None:
            raise ValueError("latitude and longitude are required")
        try:
            location = (
                self.session.query(Location).filter(Location.id == location_id).one()
            )
            location.lat = dto.latitude
            location.lng = dto.longitude
        except sqlalchemy.exc.NoResultFound:
            raise LocationDoesNotExistError

    def refresh_materialized_view(self, view_name: str):
        self.execute_raw_sql(f"REFRESH MATERIALIZED VIEW {view_name};")

    def refresh_all_materialized_views(self):
        self.execute_raw_sql(REFRESH_ALL_MATERIALIZED_VIEWS_QUERIES)

    def get_map_localities(self):
        return self.execute_raw_sql(GET_MAP_LOCALITIES_QUERY)

    def get_map_counties(self):
        return self.execute_raw_sql(GET_MAP_COUNTIES_QUERY)

    def get_map_states(self):
        return self.execute_raw_sql(GET_MAP_STATES_QUERY)

    def get_data_source_count_by_location_type(self):
        return self.execute_raw_sql(GET_DATA_SOURCE_COUNT_BY_LOCATION_TYPE_QUERY)[0]

    @session_manager
    def get_many_locations(
        self,
        page: int,
        has_coordinates: bool | None = None,
        type_: LocationType | None = None,
    ):
        builder = GetManyLocationsQueryBuilder(
            page=page,
            has_coordinates=has_coordinates,
            type_=type_,
        )
        return self.run_query_builder(builder)

    @session_manager
    def add_to_notification_log(
        self,
        user_count: int,
        dt: datetime | None = None,
    ):
        item = NotificationLog(
            user_count=user_count,
        )
        if dt is not None:
            item.created_at = dt
        self.session.add(item)

    def get_metrics_followed_searches_breakdown(
        self, dto: MetricsFollowedSearchesBreakdownRequestDTO
    ):
        builder = GetMetricsFollowedSearchesBreakdownQueryBuilder(dto=dto)
        return self.run_query_builder(builder)

    def get_metrics_followed_searches_aggregate(self):
        # TODO: QueryBuilder
        subquery_latest_notification = (
            select(NotificationLog.created_at.label("last_notification"))
            .order_by(NotificationLog.created_at.desc())
            .limit(1)
            .scalar_subquery()
        )

        statement = select(
            func.count(func.distinct(LinkUserFollowedLocation.user_id)).label(
                "total_followers"
            ),
            func.count(LinkUserFollowedLocation.location_id).label("location_count"),
            subquery_latest_notification.label("last_notification"),
        )

        result = self.one(statement)

        return {
            "total_followers": result.total_followers,
            "total_followed_searches": result.location_count,
            "last_notification_date": result.last_notification.strftime(DATE_FORMAT),
        }

    def get_duplicate_urls_bulk(self, urls: list[str]) -> Sequence:
        """Return all URLs that already exist in the database."""
        stmt = select(DistinctSourceURL.original_url).where(
            DistinctSourceURL.base_url.in_(urls)
        )
        existing_urls = self.scalars(stmt)
        return existing_urls

    def get_agencies_for_sync(
        self, dto: SourceCollectorSyncAgenciesRequestDTO
    ) -> dict[str, list[dict]]:
        """Get agencies for source collector sync."""
        builder = SourceCollectorSyncAgenciesQueryBuilder(dto=dto)
        return self.run_query_builder(builder)

    def get_data_sources_for_sync(
        self, dto: SourceCollectorSyncDataSourcesRequestDTO
    ) -> SourceCollectorSyncDataSourcesResponseDTO:
        return self.run_query_builder(
            SourceCollectorSyncDataSourcesQueryBuilder(dto=dto)
        )

    def patch_user(self, user_id: int, dto: UserPatchDTO) -> None:
        builder = UserPatchQueryBuilder(dto=dto, user_id=user_id)
        self.run_query_builder(builder)

    def validate_and_add_user(self, validation_token: str) -> str:
        """Validate pending user, add as full user, and return user email."""
        builder = ValidateEmailQueryBuilder(validation_token=validation_token)
        return self.run_query_builder(builder)
