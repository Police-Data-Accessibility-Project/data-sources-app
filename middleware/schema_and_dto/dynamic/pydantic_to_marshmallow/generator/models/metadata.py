from typing import Optional, Annotated

from pydantic import BaseModel

from utilities.enums import SourceMappingEnum


class MetadataInfo(BaseModel):
    """
    This hijacks the pydantic field json_schema_extra
    to provide a consistent interface for marshmallow metadata
    """

    source: SourceMappingEnum = SourceMappingEnum.JSON
    required: bool = True

    def get(self, key: str, default=None):
        return self.model_dump().get(key, default)
