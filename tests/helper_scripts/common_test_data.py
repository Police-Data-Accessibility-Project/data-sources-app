from http import HTTPStatus
from collections import namedtuple

ResponseTuple = namedtuple("ResponseTuple", ["response", "status_code"])

TEST_RESPONSE = ResponseTuple(response={"message": "Test Response"}, status_code=HTTPStatus.IM_A_TEAPOT)

