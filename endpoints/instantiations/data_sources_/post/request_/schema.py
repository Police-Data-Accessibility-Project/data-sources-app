from endpoints.instantiations.data_sources_.post.request_.model import (
    PostDataSourceOuterRequest,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

PostDataSourceRequestSchema = pydantic_to_marshmallow(PostDataSourceOuterRequest)
