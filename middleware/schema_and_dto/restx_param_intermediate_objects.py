from typing import Optional

from flask_restx import Namespace

from middleware.schema_and_dto.non_dto_dataclasses import FlaskRestxDocInfo


class RestxParamIntermediateObjects:
    """
    Intermediate objects used to build the restx parameter documentation
    """

    def __init__(self, namespace: Namespace, model_name: Optional[str] = None):
        self.namespace = namespace
        self.model_name = model_name
        self.parser = namespace.parser()
        self.restx_model_dict = {}

    def construct_doc_info(self) -> FlaskRestxDocInfo:
        return FlaskRestxDocInfo(
            model=self.namespace.model(self.model_name, self.restx_model_dict),
            parser=self.parser,
        )
