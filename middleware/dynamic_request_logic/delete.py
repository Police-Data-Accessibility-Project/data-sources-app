from http import HTTPStatus
from typing import Optional

from werkzeug.exceptions import Forbidden

from middleware.common_response_formatting import message_response
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.common_functions import check_for_id
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.flask_response_manager import FlaskResponseManager
from middleware.util.dynamic import call_if_not_none


def check_for_delete_permissions(check_function: DeferredFunction, entry_name: str):
    if not check_function.execute():
        raise Forbidden(f"You do not have permission to delete this {entry_name}.")


def delete_entry(
    middleware_parameters: MiddlewareParameters,
    id_info: IDInfo,
    permission_checking_function: Optional[DeferredFunction] = None,
):
    mp = middleware_parameters

    entry_id = check_for_id(
        table_name=mp.relation,
        id_info=id_info,
        db_client=mp.db_client,
    )

    call_if_not_none(
        obj=permission_checking_function,
        func=check_for_delete_permissions,
        check_function=permission_checking_function,
        entry_name=mp.entry_name,
    )

    mp.db_client_method(
        mp.db_client, id_column_name=id_info.id_column_name, id_column_value=entry_id
    )
    return message_response(f"{mp.entry_name} deleted.")
