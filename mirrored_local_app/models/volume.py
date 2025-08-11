from typing import Annotated

from pydantic import BaseModel, AfterValidator

from mirrored_local_app.helpers.path import get_absolute_path
from mirrored_local_app.helpers.check import check_for_absolute_path


class VolumeInfo(BaseModel):
    host_path: str
    container_path: Annotated[str, AfterValidator(check_for_absolute_path)]

    def build_volumes(self):
        return {
            get_absolute_path(self.host_path): {
                "bind": self.container_path,
                "mode": "rw",
            }
        }
