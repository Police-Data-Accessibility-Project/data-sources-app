from flask import Response

from db.enums import RelationRoleEnum
from middleware.common_response_formatting import message_response
from middleware.dynamic_request_logic.post import PostLogic
from middleware.primary_resource_logic.data_requests_.helpers import (
    check_has_admin_or_owner_role,
)


class CreateDataRequestRelatedLocationLogic(PostLogic):
    def check_can_edit_columns(self, relation_role: RelationRoleEnum):
        check_has_admin_or_owner_role(relation_role)

    def make_response(self) -> Response:
        return message_response("Location successfully associated with request.")
