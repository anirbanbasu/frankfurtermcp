from importlib.metadata import metadata


class EnvVar:
    """
    List of environment variables used in this project.
    """

    LOG_LEVEL = "LOG_LEVEL"
    DEFAULT__LOG_LEVEL = "INFO"

    FASTMCP_HOST = "FASTMCP_HOST"
    DEFAULT__FASTMCP_HOST = "localhost"

    FASTMCP_PORT = "FASTMCP_PORT"
    DEFAULT__FASTMCP_PORT = 8000

    MCP_SERVER_TRANSPORT = "MCP_SERVER_TRANSPORT"
    DEFAULT__MCP_SERVER_TRANSPORT = "stdio"
    ALLOWED__MCP_SERVER_TRANSPORT = ["stdio", "sse", "streamable-http"]

    MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE = "MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE"
    DEFAULT__MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE = True

    FRANKFURTER_API_URL = "FRANKFURTER_API_URL"
    DEFAULT__FRANKFURTER_API_URL = "https://api.frankfurter.dev/v1"

    HTTPX_TIMEOUT = "HTTPX_TIMEOUT"
    DEFAULT__HTTPX_TIMEOUT = 5.0

    HTTPX_VERIFY_SSL = "HTTPX_VERIFY_SSL"
    DEFAULT__HTTPX_VERIFY_SSL = True


class AppMetadata:
    """
    Metadata for the application.
    """

    PACKAGE_NAME = "frankfurtermcp"
    TEXT_CONTENT_META_PREFIX = f"{PACKAGE_NAME}."
    package_metadata = metadata(PACKAGE_NAME)
