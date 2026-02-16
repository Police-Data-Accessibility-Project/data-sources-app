import logging
from contextvars import ContextVar

is_test_request: ContextVar[bool] = ContextVar("is_test_request", default=False)


class SuppressTestAccessLogMiddleware:
    """Pure ASGI middleware that sets is_test_request contextvar when X-Test-Run header is present."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            value = headers.get(b"x-test-run", b"").lower()
            if value == b"true":
                token = is_test_request.set(True)
                try:
                    await self.app(scope, receive, send)
                finally:
                    is_test_request.reset(token)
                return
        await self.app(scope, receive, send)


class TestRequestAccessLogFilter(logging.Filter):
    """Suppresses access log entries for requests marked as test requests."""

    def filter(self, record: logging.LogRecord) -> bool:
        return not is_test_request.get(False)


def install_test_request_log_filter() -> None:
    """Attaches the TestRequestAccessLogFilter to the uvicorn.access logger."""
    logger = logging.getLogger("uvicorn.access")
    logger.addFilter(TestRequestAccessLogFilter())
