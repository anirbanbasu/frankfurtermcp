import copy
import json
import logging
import os
import ssl
from typing import Any, ClassVar

import certifi
import httpx
from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from pydantic import BaseModel, HttpUrl

from frankfurtermcp import EnvVar
from frankfurtermcp.common import AppMetadata
from frankfurtermcp.model import ResponseMetadata

logger = logging.getLogger(__name__)


class MCPMixin:
    """A mixin class to register tools, resources, and prompts with a FastMCP instance."""

    # Each entry is a dict, must include "fn" (method name),
    # rest is arbitrary metadata relevant to FastMCP.
    tools: ClassVar[list[dict[str, Any]]] = []
    # Each entry is a dict, must include "fn" (method name) and "uri",
    # rest is arbitrary metadata relevant to FastMCP.
    resources: ClassVar[list[dict[str, Any]]] = []
    # Each entry is a dict, must include "fn" (method name),
    # rest is arbitrary metadata relevant to FastMCP.
    prompts: ClassVar[list[dict[str, Any]]] = []

    frankfurter_api_url: str = EnvVar.FRANKFURTER_API_URL

    def register_features(self, mcp: FastMCP) -> FastMCP:
        """Register tools, resources, and prompts with the given FastMCP instance.

        Args:
            mcp (FastMCP): The FastMCP instance to register features with.

        Returns:
            FastMCP: The FastMCP instance with registered features.
        """
        # Register tools
        for tool in self.tools:
            assert "fn" in tool, "Tool metadata must include the 'fn' key."
            tool_copy = copy.deepcopy(tool)
            fn_name = tool_copy.pop("fn")
            fn = getattr(self, fn_name)
            mcp.tool(**tool_copy)(fn)
            logger.debug(f"Registered MCP tool: {fn_name}")
        # Register resources
        for res in self.resources:  # pragma: no cover
            assert "fn" in res and "uri" in res, "Resource metadata must include 'fn' and 'uri' keys."
            res_copy = copy.deepcopy(res)
            fn_name = res_copy.pop("fn")
            uri = res_copy.pop("uri")
            fn = getattr(self, fn_name)
            mcp.resource(uri, **res_copy)(fn)
            logger.debug(f"Registered MCP resource at URI: {uri}")
        # Register prompts
        for pr in self.prompts:  # pragma: no cover
            assert "fn" in pr, "Prompt metadata must include the 'fn' key."
            pr_copy = copy.deepcopy(pr)
            fn_name = pr_copy.pop("fn")
            fn = getattr(self, fn_name)
            mcp.prompt(**pr_copy)(fn)
            logger.debug(f"Registered MCP prompt: {fn_name}")

        return mcp

    def get_response_content(
        self,
        response: Any,
        http_response: httpx.Response | None = None,
        include_metadata: bool = EnvVar.MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE,
        cached_response: bool = False,
    ) -> ToolResult:
        """Convert response data to a ToolResult format with optional metadata.

        Args:
            response (Any): The response data to convert.
            http_response (httpx.Response): The HTTP response object for header extraction.
            include_metadata (bool): Whether to include metadata in the response.
            cached_response (bool): Indicates if the response was served from cache, which will be reflected in metadata.

        Returns:
            ToolResult: The ToolResult enclosing the TextContent representation of the response
            along with metadata if requested.
        """
        literal_text = "text"
        text_content: TextContent | None = None
        structured_content: dict[str, Any] | None = None
        if isinstance(response, TextContent):  # pragma: no cover
            text_content = response
            structured_content = {"result": response.text}
        elif isinstance(response, (str, int, float, complex, bool, type(None))):  # pragma: no cover
            text_content = TextContent(type=literal_text, text=str(response))
            structured_content = {"result": response}
        elif isinstance(response, list):  # pragma: no cover
            text_content = TextContent(type=literal_text, text=json.dumps(response))
            structured_content = {"result": response}
        elif isinstance(response, dict):
            structured_content = response
        elif isinstance(response, BaseModel):
            structured_content = response.model_dump()
        else:  # pragma: no cover
            raise TypeError(
                f"Unsupported data type: {type(response).__name__}. "
                "Only str, int, float, complex, bool, dict, list, and Pydantic BaseModel types are supported."
            )
        if text_content is not None:
            tool_result = ToolResult(content=[text_content], structured_content=structured_content)
        elif structured_content is not None:
            tool_result = ToolResult(content=structured_content)
        else:
            assert False, (
                "Unreachable code reached in get_response_content. "
                "Both text_content and structured_content should not have been None."
            )
        if include_metadata:
            tool_result.meta = {
                AppMetadata.PACKAGE_NAME: ResponseMetadata(
                    version=AppMetadata.package_metadata["Version"],
                    api_url=HttpUrl(self.frankfurter_api_url) if http_response else None,
                    api_status_code=http_response.status_code if http_response else None,
                    api_bytes_downloaded=http_response.num_bytes_downloaded if http_response else None,
                    api_elapsed_time=http_response.elapsed.microseconds if http_response else None,
                    cached_response=cached_response,
                ).model_dump(),
            }
        return tool_result


class HTTPHelperMixin:
    """A mixin class to provide HTTP client functionality using httpx."""

    def get_httpx_client(self) -> httpx.Client:
        """Obtain an HTTPX client for making requests."""
        verify = EnvVar.HTTPX_VERIFY_SSL
        if verify is False:  # pragma: no cover
            logging.warning("SSL verification is disabled. This is not recommended for production use.")
        ctx = ssl.create_default_context(
            cafile=os.environ.get("SSL_CERT_FILE", certifi.where()),
            capath=os.environ.get("SSL_CERT_DIR"),
        )
        client = httpx.Client(
            verify=verify if (verify is not None and verify is False) else ctx,
            follow_redirects=True,
            trust_env=True,
            timeout=EnvVar.HTTPX_TIMEOUT,
        )
        return client
