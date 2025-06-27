try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


import json
from dotenv import load_dotenv

from fastmcp import Client

from importlib.metadata import metadata

import httpx
from mcp.types import TextContent

import os
from typing import Annotated, Any

from pydantic import BaseModel, Field

SPACE_STRING = " "
TRUE_VALUES_LIST = ["true", "1", "yes", "on", "yes", "y", "t"]
FALSE_VALUES_LIST = ["false", "0", "no", "off", "n", "f"]


class EnvironmentVariables:
    """
    List of environment variables used in this project.
    """

    MCP_SERVER_HOST = "FASTMCP_HOST"
    DEFAULT__MCP_SERVER_HOST = "localhost"

    MCP_SERVER_PORT = "FASTMCP_PORT"
    DEFAULT__MCP_SERVER_PORT = 8000

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

    TEXT_CONTENT_META_PREFIX = "frankfurtermcp."


package_metadata = metadata(AppMetadata.PACKAGE_NAME)


class ResponseMetadata(BaseModel):
    """
    Metadata for the TextContent response.
    """

    version: Annotated[str, Field(description="The version of the package.")]
    api_url: Annotated[
        str,
        Field(description="The URL of the Frankfurter API used for the call."),
    ]
    api_status_code: Annotated[
        int, Field(description="The HTTP status code of the API response.")
    ]
    api_bytes_downloaded: Annotated[
        int, Field(description="The number of bytes downloaded in the API response.")
    ]
    api_elapsed_time: Annotated[
        int, Field(description="The elapsed time for the API call in microseconds.")
    ]


class CurrencyConversionResponse(BaseModel):
    """
    Response model for currency conversion.
    """

    from_currency: Annotated[str, Field(description="The currency to convert from.")]
    to_currency: Annotated[str, Field(description="The currency to convert to.")]
    amount: Annotated[
        float, Field(description="The amount (of the source currency) to convert.")
    ]
    converted_amount: Annotated[
        float, Field(description="The converted amount (of the target currency).")
    ]
    exchange_rate: Annotated[
        float, Field(description="The exchange rate used for the conversion.")
    ]
    rate_date: Annotated[
        str,
        Field(
            description="The date, ISO format, of the exchange rate used for the conversion."
        ),
    ]


load_dotenv()


def parse_env(
    var_name: str,
    default_value: Any | None = None,
    allowed_values: list[Any] | None = None,
    type_cast: type = str,
    convert_to_list=False,
    list_split_char=SPACE_STRING,
) -> Any | list[Any]:
    """
    Parse the environment variable and return the value.

    Args:
        var_name (str): The name of the environment variable.
        default_value (Any | None): The default value to use if the environment variable is not set. Defaults to None.
        allowed_values (list[Any] | None): A list of allowed values for the environment variable. If provided, the
            value will be checked against this list. This option is ignored if type_cast is bool.
        type_cast (type): The type to cast the value to.
        convert_to_list (bool): Whether to convert the value to a list.
        list_split_char (str): The character to split the list on.

    Returns:
        (Any | list[Any]) The parsed value, either as a single value or a list. The type of the returned single
        value or individual elements in the list depends on the supplied type_cast parameter.
    """
    if default_value is not None and not isinstance(default_value, type_cast):
        raise TypeError(
            f"The default value {default_value} specified for the environment variable {var_name} is of type {type(default_value).__name__}. However, the expected type is {type_cast.__name__} instead."
        )
    if os.getenv(var_name) is None and default_value is None:
        raise ValueError(
            f"Environment variable {var_name} does not exist and a default value has not been provided."
        )
    parsed_value = None
    if type_cast is bool:
        # Sometimes, the environment variable is set to a string that represents a boolean value.
        # We convert it to lowercase and check against TRUE_VALUES_LIST.
        # The following logic also works if the boolean value is set to a True or False boolean type.
        parsed_value = (
            str(os.getenv(var_name, default_value)).lower() in TRUE_VALUES_LIST
        )
    else:
        parsed_value = os.getenv(var_name, default_value)
        if allowed_values is not None:
            if parsed_value not in allowed_values:
                raise ValueError(
                    f"Environment variable {var_name} has value '{parsed_value}', "
                    f"which is not in the allowed values: {allowed_values}."
                )

    if not convert_to_list:
        value: Any = (
            type_cast(parsed_value)
            if not isinstance(parsed_value, type_cast)
            else parsed_value
        )
    else:
        value: list[Any] = [
            (type_cast(v) if not isinstance(v, type_cast) else v)
            for v in parsed_value.split(list_split_char)
        ]
    return value


frankfurter_api_url = parse_env(
    EnvironmentVariables.FRANKFURTER_API_URL,
    default_value=EnvironmentVariables.DEFAULT__FRANKFURTER_API_URL,
)


def get_nonstdio_transport_endpoint() -> str:
    """
    Get the transport endpoint for the non-stdio MCP client based on environment variables.
    """
    transport_type = parse_env(
        EnvironmentVariables.MCP_SERVER_TRANSPORT,
        default_value=EnvironmentVariables.DEFAULT__MCP_SERVER_TRANSPORT,
        allowed_values=EnvironmentVariables.ALLOWED__MCP_SERVER_TRANSPORT,
    )
    transport_endpoint = None
    server_host = parse_env(
        "FASTMCP_HOST",
        default_value="localhost",
    )
    server_port = parse_env(
        "FASTMCP_PORT",
        default_value=8000,
        type_cast=int,
    )
    if transport_type == "streamable-http":
        transport_endpoint = f"http://{server_host}:{server_port}/mcp"
    elif transport_type == "sse":
        transport_endpoint = f"http://{server_host}:{server_port}/sse"
    else:
        raise ValueError(
            f"Unsupported transport type: {transport_type}. "
            "Allowed values are for this type of client are only sse and streamable-http: "
        )
    return transport_endpoint


def get_nonstdio_mcp_client() -> Client:
    """
    Create and return a non-stdio MCP client to connect to built-in server based on the environment variables.
    """
    transport_endpoint = get_nonstdio_transport_endpoint()
    mcp_client = Client(
        transport=transport_endpoint,
        timeout=60,
    )
    return mcp_client


def get_text_content(
    data: Any,
    http_response: httpx.Response,
    include_metadata: bool = parse_env(
        var_name=EnvironmentVariables.MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE,
        default_value=EnvironmentVariables.DEFAULT__MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE,
        type_cast=bool,
    ),
) -> TextContent:
    """
    Convert data to TextContent format.

    Args:
        data (Any): The data to convert.
        include_metadata (bool): Whether to include metadata in the TextContent.

    Returns:
        TextContent: The converted TextContent object.
    """
    literal_text = "text"
    if isinstance(data, TextContent):
        # do nothing yet
        pass
    elif isinstance(data, (str, int, float, complex, bool, type(None))):
        text_content = TextContent(type=literal_text, text=str(data))
    elif isinstance(data, dict) or isinstance(data, list):
        text_content = TextContent(type=literal_text, text=json.dumps(data))
    elif isinstance(data, BaseModel):
        text_content = TextContent(type=literal_text, text=data.model_dump_json())
    else:
        raise TypeError(
            f"Unsupported data type: {type(data).__name__}. "
            "Only str, int, float, complex, bool, dict, list, and Pydantic BaseModel types are supported for wrapping as TextContent."
        )
    if include_metadata:
        text_content.meta = text_content.meta if hasattr(text_content, "meta") else {}
        text_content.meta[AppMetadata.PACKAGE_NAME] = ResponseMetadata(
            version=package_metadata["Version"],
            api_url=frankfurter_api_url,
            api_status_code=http_response.status_code,
            api_bytes_downloaded=http_response.num_bytes_downloaded,
            api_elapsed_time=http_response.elapsed.microseconds,
        ).model_dump()
    return text_content
