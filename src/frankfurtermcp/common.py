from importlib.metadata import metadata


from enum import Enum, auto


class AllCapsStrEnum(str, Enum):
    # See https://github.com/python/cpython/issues/115509#issuecomment-1946971056
    @staticmethod
    def _generate_next_value_(name, *args):
        return name.upper()


class EnvironmentVariables(AllCapsStrEnum):
    """
    List of environment variables used in this project.
    """

    LOG_LEVEL = auto()
    DEFAULT__LOG_LEVEL = "INFO"

    FASTMCP_HOST = auto()
    DEFAULT__FASTMCP_HOST = "localhost"

    FASTMCP_PORT = auto()
    DEFAULT__FASTMCP_PORT = 8000

    MCP_SERVER_TRANSPORT = auto()
    DEFAULT__MCP_SERVER_TRANSPORT = "stdio"
    ALLOWED__MCP_SERVER_TRANSPORT = ["stdio", "sse", "streamable-http"]

    MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE = "MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE"
    DEFAULT__MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE = True

    FRANKFURTER_API_URL = auto()
    DEFAULT__FRANKFURTER_API_URL = "https://api.frankfurter.dev/v1"

    HTTPX_TIMEOUT = auto()
    DEFAULT__HTTPX_TIMEOUT = 5.0

    HTTPX_VERIFY_SSL = auto()
    DEFAULT__HTTPX_VERIFY_SSL = True


class AppMetadata:
    """
    Metadata for the application.
    """

    PACKAGE_NAME = "frankfurtermcp"
    TEXT_CONTENT_META_PREFIX = f"{PACKAGE_NAME}."
    package_metadata = metadata(PACKAGE_NAME)
