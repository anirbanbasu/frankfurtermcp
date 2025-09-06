import json
import logging
import os
import ssl
from typing import Any, ClassVar, Dict, List

import certifi
from fastmcp import FastMCP
import copy

import httpx
from mcp.types import TextContent
from pydantic import BaseModel

from frankfurtermcp.common import AppMetadata, EnvVar
from frankfurtermcp.model import ResponseMetadata

from frankfurtermcp import env

logger = logging.getLogger(__name__)


class MCPMixin:
    """
    A mixin class to register tools, resources, and prompts with a FastMCP instance.
    """

    # Each entry is a dict, must include "fn" (method name),
    # rest is arbitrary metadata relevant to FastMCP.
    tools: ClassVar[List[Dict[str, Any]]] = []
    # Each entry is a dict, must include "fn" (method name) and "uri",
    # rest is arbitrary metadata relevant to FastMCP.
    resources: ClassVar[List[Dict[str, Any]]] = []
    # Each entry is a dict, must include "fn" (method name),
    # rest is arbitrary metadata relevant to FastMCP.
    prompts: ClassVar[List[Dict[str, Any]]] = []

    frankfurter_api_url: ClassVar[str] = env.str(
        name=EnvVar.FRANKFURTER_API_URL,
        default=EnvVar.DEFAULT__FRANKFURTER_API_URL,
    )

    def register_features(self, mcp: FastMCP) -> FastMCP:
        """
        Register tools, resources, and prompts with the given FastMCP instance.

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
            mcp.tool(**tool_copy)(fn)  # pass remaining metadata as kwargs
            logger.debug(f"Registered MCP tool: {fn_name}")
        # Register resources
        for res in self.resources:  # pragma: no cover
            assert "fn" in res and "uri" in res, (
                "Resource metadata must include 'fn' and 'uri' keys."
            )
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

    def get_response_text_content(
        self,
        response: Any,
        http_response: httpx.Response,
        include_metadata: bool = env.bool(
            name=EnvVar.MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE,
            default=EnvVar.DEFAULT__MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE,
        ),
    ) -> TextContent:
        """
        Convert response data to TextContent format.

        Args:
            response (Any): The response data to convert.
            http_response (httpx.Response): The HTTP response object for header extraction.
            include_metadata (bool): Whether to include metadata in the TextContent.

        Returns:
            TextContent: The converted TextContent object.
        """
        literal_text = "text"
        if isinstance(response, TextContent):
            # do nothing yet
            pass
        elif isinstance(response, (str, int, float, complex, bool, type(None))):
            text_content = TextContent(type=literal_text, text=str(response))
        elif isinstance(response, dict) or isinstance(response, list):
            text_content = TextContent(type=literal_text, text=json.dumps(response))
        elif isinstance(response, BaseModel):
            text_content = TextContent(
                type=literal_text, text=response.model_dump_json()
            )
        else:
            raise TypeError(
                f"Unsupported data type: {type(response).__name__}. "
                "Only str, int, float, complex, bool, dict, list, and Pydantic BaseModel types are supported for wrapping as TextContent."
            )
        if include_metadata:
            text_content.meta = (
                text_content.meta if hasattr(text_content, "_meta") else {}
            )
            text_content.meta[AppMetadata.PACKAGE_NAME] = ResponseMetadata(
                version=AppMetadata.package_metadata["Version"],
                api_url=self.frankfurter_api_url,
                api_status_code=http_response.status_code,
                api_bytes_downloaded=http_response.num_bytes_downloaded,
                api_elapsed_time=http_response.elapsed.microseconds,
            ).model_dump()
        return text_content


class HTTPHelperMixin:
    """
    A mixin class to provide HTTP client functionality using httpx.
    """

    def get_httpx_client(self) -> httpx.Client:
        """
        Obtain an HTTPX client for making requests.
        """
        verify = env.bool(
            name=EnvVar.HTTPX_VERIFY_SSL,
            default=EnvVar.DEFAULT__HTTPX_VERIFY_SSL,
        )
        if verify is False:
            logging.warning(
                "SSL verification is disabled. This is not recommended for production use."
            )
        ctx = ssl.create_default_context(
            cafile=os.environ.get("SSL_CERT_FILE", certifi.where()),
            capath=os.environ.get("SSL_CERT_DIR"),
        )
        client = httpx.Client(
            verify=verify if (verify is not None and verify is False) else ctx,
            follow_redirects=True,
            trust_env=True,
            timeout=env.float(
                name=EnvVar.HTTPX_TIMEOUT,
                default=EnvVar.DEFAULT__HTTPX_TIMEOUT,
            ),
        )
        return client
