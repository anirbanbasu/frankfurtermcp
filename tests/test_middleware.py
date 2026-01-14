import asyncio
import logging

import pytest
from fastmcp import Client, FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from frankfurtermcp.middleware import RequestSizeLimitMiddleware, StripUnknownArgumentsMiddleware
from frankfurtermcp.server import FrankfurterMCP


class TestStripUnknownArgumentsMiddleware:
    """Dedicated test class for the StripUnknownArgumentsMiddleware."""

    @pytest.fixture(scope="class")
    @classmethod
    def mcp_server(cls):
        """Fixture to create an MCP server instance with the middleware."""
        server = FastMCP()
        mcp_obj = FrankfurterMCP()
        server_with_features = mcp_obj.register_features(server)
        server_with_features.add_middleware(StripUnknownArgumentsMiddleware())
        return server_with_features

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def mcp_client(cls, mcp_server):
        """Fixture to create a client for the MCP server."""
        mcp_client = Client(transport=mcp_server, timeout=60)
        return mcp_client

    async def call_tool(self, tool_name: str, mcp_client: Client, **kwargs):
        """Helper method to call a tool on the MCP server."""
        async with mcp_client:
            result = await mcp_client.call_tool(tool_name, arguments=kwargs)
            await mcp_client.close()
        return result

    def test_strip_unknown_arguments(self, mcp_client: Client, caplog):
        """Test that unknown arguments are stripped from tool calls and logged."""
        tool_name = "greet"
        valid_name = "Test User"
        unknown_arg_value = "This should be stripped"

        with caplog.at_level(logging.INFO):
            results = asyncio.run(
                self.call_tool(
                    tool_name,
                    mcp_client,
                    name=valid_name,
                    unknown_argument=unknown_arg_value,
                )
            )

        # Verify the tool call succeeded with valid argument
        assert hasattr(results, "content"), "Expected results to have 'content' attribute"
        assert hasattr(results, "structured_content"), "Expected results to have 'structured_content' attribute"
        assert "result" in results.structured_content, "Expected 'structured_content' to have 'result' key"

        # Verify the greeting contains the valid name (proving valid args passed through)
        greeting = results.structured_content["result"]
        assert valid_name in greeting, f"Expected greeting to contain '{valid_name}'"

        # Verify logging occurred for unknown arguments
        assert any("Unknown arguments for tool 'greet'" in record.message for record in caplog.records), (
            "Expected logging of unknown arguments"
        )

        # Verify the unknown argument was identified in the logs
        assert any("unknown_argument" in record.message for record in caplog.records), (
            "Expected 'unknown_argument' to be logged as unknown"
        )

    def test_all_arguments_unknown(self, mcp_client: Client, caplog):
        """Test behavior when all provided arguments are unknown."""
        tool_name = "greet"

        with caplog.at_level(logging.INFO):
            results = asyncio.run(
                self.call_tool(
                    tool_name,
                    mcp_client,
                    completely_unknown_arg="value1",
                    another_unknown_arg="value2",
                )
            )

        # Verify the tool call still succeeds (using defaults)
        assert hasattr(results, "content"), "Expected results to have 'content' attribute"
        assert hasattr(results, "structured_content"), "Expected results to have 'structured_content' attribute"
        assert "result" in results.structured_content, "Expected 'structured_content' to have 'result' key"

        # Verify default greeting (no name provided)
        greeting = results.structured_content["result"]
        assert "World" in greeting, "Expected default greeting with 'World'"

        # Verify logging occurred
        assert any("Unknown arguments for tool 'greet'" in record.message for record in caplog.records), (
            "Expected logging of unknown arguments"
        )

    def test_no_arguments_provided(self, mcp_client: Client, caplog):
        """Test that middleware handles tools called with no arguments correctly."""
        tool_name = "greet"

        with caplog.at_level(logging.INFO):
            results = asyncio.run(self.call_tool(tool_name, mcp_client))

        # Verify the tool call succeeds
        assert hasattr(results, "content"), "Expected results to have 'content' attribute"
        assert hasattr(results, "structured_content"), "Expected results to have 'structured_content' attribute"

        # Verify no middleware logging for this case (no args to strip)
        middleware_logs = [record for record in caplog.records if "Unknown arguments" in record.message]
        assert len(middleware_logs) == 0, "Expected no middleware logging when no arguments provided"

    def test_only_valid_arguments(self, mcp_client: Client, caplog):
        """Test that middleware doesn't interfere when only valid arguments are provided."""
        tool_name = "greet"
        valid_name = "Valid User"

        with caplog.at_level(logging.INFO):
            results = asyncio.run(self.call_tool(tool_name, mcp_client, name=valid_name))

        # Verify the tool call succeeds with the valid argument
        assert hasattr(results, "content"), "Expected results to have 'content' attribute"
        greeting = results.structured_content["result"]
        assert valid_name in greeting, f"Expected greeting to contain '{valid_name}'"

        # Verify no unknown argument logging
        unknown_arg_logs = [record for record in caplog.records if "Unknown arguments" in record.message]
        assert len(unknown_arg_logs) == 0, "Expected no unknown argument logging for valid args only"

    def test_mixed_valid_and_unknown_arguments(self, mcp_client: Client, caplog):
        """Test middleware behavior with a mix of valid and unknown arguments."""
        tool_name = "greet"
        valid_name = "Mixed Test"

        with caplog.at_level(logging.INFO):
            results = asyncio.run(
                self.call_tool(
                    tool_name,
                    mcp_client,
                    name=valid_name,
                    unknown1="value1",
                    unknown2={"key": "value2"},
                    unknown3=3.14,
                )
            )

        # Verify valid argument was used
        greeting = results.structured_content["result"]
        assert valid_name in greeting, f"Expected greeting to contain '{valid_name}'"

        # Verify multiple unknown arguments are logged
        unknown_logs = [record for record in caplog.records if "Unknown arguments for tool 'greet'" in record.message]
        assert len(unknown_logs) > 0, "Expected logging for unknown arguments"

        # Verify all three unknown arguments are mentioned
        log_messages = " ".join([record.message for record in caplog.records])
        assert "unknown1" in log_messages, "Expected 'unknown1' in logs"
        assert "unknown2" in log_messages, "Expected 'unknown2' in logs"
        assert "unknown3" in log_messages, "Expected 'unknown3' in logs"


class TestRequestSizeLimitMiddleware:
    """Dedicated test class for the RequestSizeLimitMiddleware."""

    @pytest.fixture
    def app(self):
        """Fixture to create a Starlette app with RequestSizeLimitMiddleware."""

        async def test_endpoint(request: Request):
            """Test endpoint that returns request body size."""
            body = await request.body()
            return JSONResponse({"size": len(body), "message": "success"})

        app = Starlette(
            routes=[Route("/test", test_endpoint, methods=["POST"])],
            middleware=[
                Middleware(RequestSizeLimitMiddleware, max_body_size=1024)  # 1KB limit for testing
            ],
        )
        return app

    @pytest.fixture
    def client(self, app):
        """Fixture to create a test client."""
        return TestClient(app)

    def test_request_within_size_limit(self, client):
        """Test that requests within the size limit are processed successfully."""
        # Create a payload smaller than the 1KB limit
        payload = "x" * 512  # 512 bytes
        response = client.post("/test", content=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["size"] == 512
        assert data["message"] == "success"

    def test_request_exactly_at_size_limit(self, client):
        """Test that requests exactly at the size limit are processed successfully."""
        # Create a payload exactly at the 1KB limit
        payload = "x" * 1024  # 1024 bytes
        response = client.post("/test", content=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["size"] == 1024
        assert data["message"] == "success"

    def test_request_exceeds_size_limit(self, client):
        """Test that requests exceeding the size limit are rejected with 413."""
        # Create a payload larger than the 1KB limit
        payload = "x" * 2048  # 2048 bytes
        response = client.post("/test", content=payload)

        assert response.status_code == 413
        assert response.text == "Request body is too large. Allowed maximum size is 1024 bytes."

    def test_request_without_content_length(self, client):
        """Test that requests without Content-Length header are processed normally."""
        # Requests without Content-Length header should pass through
        # TestClient should still set Content-Length, so we test with empty body
        response = client.post("/test", content="")

        assert response.status_code == 200
        data = response.json()
        assert data["size"] == 0

    def test_large_request_far_exceeds_limit(self, client):
        """Test that very large requests are rejected."""
        # Create a payload much larger than the limit
        payload = "x" * 10240  # 10KB, much larger than 1KB limit
        response = client.post("/test", content=payload)

        assert response.status_code == 413
        assert response.text == "Request body is too large. Allowed maximum size is 1024 bytes."
