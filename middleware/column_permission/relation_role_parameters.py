from pydantic import BaseModel, ConfigDict

from db.enums import RelationRoleEnum
from middleware.security.access_info.helpers import get_relation_role
from middleware.custom_dataclasses import DeferredFunction
from middleware.security.access_info.primary import AccessInfoPrimary


class RelationRoleParameters(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    relation_role_function_with_params: DeferredFunction = DeferredFunction(
        function=get_relation_role,
    )
    relation_role_override: RelationRoleEnum | None = None

    def get_relation_role_from_parameters(
        self, access_info: AccessInfoPrimary
    ) -> RelationRoleEnum:
        if self.relation_role_override is not None:
            return self.relation_role_override
        return self.relation_role_function_with_params.execute(access_info=access_info)
