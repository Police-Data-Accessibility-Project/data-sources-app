from dataclasses import dataclass
from http import HTTPStatus
from io import BytesIO

from marshmallow import Schema, ValidationError
from werkzeug.datastructures import FileStorage

from database_client.database_client import DatabaseClient
from middleware.dynamic_request_logic.supporting_classes import (
    PutPostRequestInfo,
    PostPutHandler,
)
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.agencies import (
    AgencyPostRequestInfo,
    AgencyPostHandler,
    AgencyPutHandler,
)
from middleware.primary_resource_logic.data_sources_logic import (
    DataSourcesPostHandler,
    DataSourcesPutHandler,
)
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_csv_to_schema_conversion_logic import (
    SchemaUnflattener,
)
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_request_content_population import (
    setup_dto_class,
)

from middleware.schema_and_dto_logic.primary_resource_dtos.bulk_dtos import (
    BulkRequestDTO,
)
from csv import DictReader

from middleware.util import bytes_to_text_iter, read_from_csv


def replace_empty_strings_with_none(row: dict):
    for key, value in row.items():
        if value == "":
            row[key] = None


def _get_raw_rows_from_csv(
    file: BytesIO,
):
    _abort_if_csv(file)
    raw_rows = _get_raw_rows(file)
    return raw_rows


def _get_raw_rows(file: FileStorage):
    try:
        return read_from_csv(file)
    except Exception as e:
        FlaskResponseManager.abort(
            code=HTTPStatus.BAD_REQUEST, message=f"Error reading csv file: {e}"
        )


def _abort_if_csv(file):
    if file.filename.split(".")[-1] != "csv":
        FlaskResponseManager.abort(
            code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, message="File must be of type csv"
        )


class BulkRequestManager:

    def __init__(self):
        self.requests = []

    def add_request(self, request: PutPostRequestInfo):
        self.requests.append(request)

    def get_requests_with_error(self):
        return [
            request for request in self.requests if request.error_message is not None
        ]

    def get_requests_without_error(self):
        return [request for request in self.requests if request.error_message is None]

    def get_error_dict(self):
        d = {}
        for request in self.requests:
            if request.error_message is not None:
                d[request.request_id] = request.error_message
        return d

    def all_requests_errored_out(self):
        return len(self.get_requests_without_error()) == 0


class BulkRowProcessor:

    def __init__(self, raw_row: dict, request_id: int):
        self.raw_row = raw_row
        self.request_id = request_id
        self.request = None
        if "id" in raw_row:
            self.entry_id = raw_row["id"]
        else:
            self.entry_id = None

    def create_request_info_with_error(self, error_message: str):
        request = PutPostRequestInfo(
            request_id=self.request_id,
            entry=self.raw_row,
            error_message=error_message,
            dto=None,
        )
        return request

    def process(
        self, unflattener: SchemaUnflattener, inner_dto_class: type, schema: Schema
    ):
        try:
            replace_empty_strings_with_none(row=self.raw_row)
            loaded_row = schema.load(self.raw_row)
        except ValidationError as e:
            # Handle validation error
            self.request = self.create_request_info_with_error(error_message=str(e))
            return
        unflattened_row = unflattener.unflatten(flat_data=loaded_row)
        inner_dto = setup_dto_class(
            data=unflattened_row,
            dto_class=inner_dto_class,
            nested_dto_info_list=unflattener.nested_dto_info_list,
        )
        self.request = self.create_completed_request(inner_dto)

    def create_completed_request(self, inner_dto):
        return PutPostRequestInfo(
            request_id=self.request_id,
            entry=dict(inner_dto),
            dto=inner_dto,
            entry_id=self.entry_id,
        )


class AgenciesPostBRP(BulkRowProcessor):

    def create_completed_request(self, inner_dto):
        return AgencyPostRequestInfo(
            request_id=self.request_id, entry=dict(inner_dto.agency_info), dto=inner_dto
        )


@dataclass
class BulkConfig:
    dto: BulkRequestDTO
    handler: PostPutHandler
    brp_class: type[BulkRowProcessor]
    schema: Schema


def listify_strings(raw_rows: list[dict]):
    for raw_row in raw_rows:
        for k, v in raw_row.items():
            if isinstance(v, str) and "," in v:
                raw_row[k] = v.split(",")


def run_bulk(
    bulk_config: BulkConfig,
):
    unflattener = SchemaUnflattener(
        flat_schema_class=bulk_config.dto.csv_schema.__class__
    )
    raw_rows = _get_raw_rows_from_csv(file=bulk_config.dto.file)
    listify_strings(raw_rows)
    schema = bulk_config.schema
    brm = BulkRequestManager()
    for idx, raw_row in enumerate(raw_rows):
        brp = bulk_config.brp_class(raw_row=raw_row, request_id=idx)
        brp.process(
            unflattener=unflattener,
            inner_dto_class=bulk_config.dto.inner_dto_class,
            schema=schema,
        )
        brm.add_request(request=brp.request)

    handler = bulk_config.handler
    handler.mass_execute(requests=brm.get_requests_without_error())
    return brm


def manage_response(
    brm: BulkRequestManager, resource_name: str, verb: str, include_ids: bool = True
):
    errors = brm.get_error_dict()
    if brm.all_requests_errored_out():
        return FlaskResponseManager.make_response(
            status_code=HTTPStatus.OK,
            data={
                "message": f"No {resource_name} were {verb} from the provided csv file.",
                "errors": errors,
            },
        )

    if include_ids:
        kwargs = {
            "ids": [request.entry_id for request in brm.get_requests_without_error()]
        }
    else:
        kwargs = {}

    return FlaskResponseManager.make_response(
        status_code=HTTPStatus.OK,
        data={
            "message": f"At least some {resource_name} created successfully.",
            "errors": errors,
            **kwargs,
        },
    )


def bulk_post_agencies(db_client: DatabaseClient, dto: BulkRequestDTO):
    brm = run_bulk(
        bulk_config=BulkConfig(
            dto=dto,
            handler=AgencyPostHandler(),
            brp_class=AgenciesPostBRP,
            schema=dto.csv_schema.__class__(exclude=["file"]),
        )
    )
    return manage_response(brm=brm, resource_name="agencies", verb="created")


def bulk_put_agencies(db_client: DatabaseClient, dto: BulkRequestDTO):
    brm = run_bulk(
        bulk_config=BulkConfig(
            dto=dto,
            handler=AgencyPutHandler(),
            brp_class=BulkRowProcessor,
            schema=dto.csv_schema.__class__(exclude=["file"]),
        )
    )
    return manage_response(
        brm=brm, resource_name="agencies", verb="updated", include_ids=False
    )


def bulk_post_data_sources(db_client: DatabaseClient, dto: BulkRequestDTO):
    brm = run_bulk(
        bulk_config=BulkConfig(
            dto=dto,
            handler=DataSourcesPostHandler(),
            brp_class=BulkRowProcessor,
            schema=dto.csv_schema.__class__(exclude=["file"]),
        )
    )
    return manage_response(brm=brm, resource_name="data sources", verb="created")


def bulk_put_data_sources(db_client: DatabaseClient, dto: BulkRequestDTO):
    brm = run_bulk(
        bulk_config=BulkConfig(
            dto=dto,
            handler=DataSourcesPutHandler(),
            brp_class=BulkRowProcessor,
            schema=dto.csv_schema.__class__(exclude=["file"]),
        )
    )
    return manage_response(
        brm=brm, resource_name="data_sources", verb="updated", include_ids=False
    )
