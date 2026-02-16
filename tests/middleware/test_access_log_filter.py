import asyncio
import logging

from middleware.access_log_filter import (
    TestRequestAccessLogFilter,
    SuppressTestAccessLogMiddleware,
    install_test_request_log_filter,
    is_test_request,
)


# --- TestRequestAccessLogFilter tests ---


class TestTestRequestAccessLogFilter:
    def test_normal_request_passes(self):
        f = TestRequestAccessLogFilter()
        record = logging.LogRecord("uvicorn.access", logging.INFO, "", 0, "GET /", (), None)
        assert f.filter(record) is True

    def test_test_request_suppressed(self):
        f = TestRequestAccessLogFilter()
        token = is_test_request.set(True)
        try:
            record = logging.LogRecord("uvicorn.access", logging.INFO, "", 0, "GET /", (), None)
            assert f.filter(record) is False
        finally:
            is_test_request.reset(token)

    def test_default_contextvar_passes(self):
        f = TestRequestAccessLogFilter()
        # Without setting the contextvar, default is False → filter passes
        record = logging.LogRecord("uvicorn.access", logging.INFO, "", 0, "GET /", (), None)
        assert f.filter(record) is True


# --- SuppressTestAccessLogMiddleware tests ---


async def _run_middleware(headers: list[tuple[bytes, bytes]], scope_type: str = "http"):
    """Helper that runs the middleware and returns the contextvar value seen by the inner app."""
    captured: dict[str, bool | None] = {"value": None}

    async def inner_app(scope, receive, send):
        captured["value"] = is_test_request.get(False)

    middleware = SuppressTestAccessLogMiddleware(inner_app)
    scope = {"type": scope_type, "headers": headers}
    await middleware(scope, None, None)
    return captured["value"]


class TestSuppressTestAccessLogMiddleware:
    def test_header_present_sets_contextvar(self):
        result = asyncio.run(
            _run_middleware([(b"x-test-run", b"true")])
        )
        assert result is True

    def test_header_absent_leaves_contextvar_false(self):
        result = asyncio.run(
            _run_middleware([])
        )
        assert result is False

    def test_non_http_scope_passes_through(self):
        result = asyncio.run(
            _run_middleware([], scope_type="websocket")
        )
        assert result is False

    def test_case_insensitive_value(self):
        result = asyncio.run(
            _run_middleware([(b"x-test-run", b"True")])
        )
        assert result is True

    def test_contextvar_reset_after_request(self):
        """Ensure the contextvar is reset after the middleware completes."""
        asyncio.run(
            _run_middleware([(b"x-test-run", b"true")])
        )
        assert is_test_request.get(False) is False


# --- install_test_request_log_filter tests ---


class TestInstallTestRequestLogFilter:
    def test_installs_filter_on_uvicorn_access_logger(self):
        logger = logging.getLogger("uvicorn.access")
        initial_count = len(logger.filters)
        install_test_request_log_filter()
        assert len(logger.filters) == initial_count + 1
        assert isinstance(logger.filters[-1], TestRequestAccessLogFilter)
        # Clean up
        logger.removeFilter(logger.filters[-1])
