[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=3776ab&labelColor=e4e4e4)](https://www.python.org/downloads/release/python-3120/) [![Dependabot Updates](https://github.com/anirbanbasu/frankfurtermcp/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/anirbanbasu/frankfurtermcp/actions/workflows/dependabot/dependabot-updates) [![pytest](https://github.com/anirbanbasu/frankfurtermcp/actions/workflows/uv-pytest.yml/badge.svg)](https://github.com/anirbanbasu/frankfurtermcp/actions/workflows/uv-pytest.yml)

# Frankfurter MCP

[Frankfurter](https://frankfurter.dev/) is a useful API for latest currency exchange rates, historical data, or time series published by sources such as the European Central Bank. Should you have to access the Frankfurter API as tools for language model agents exposed over the Model Context Protocol (MCP), Frankfurter MCP is what you need.

## Project status

Following is a table of some updates regarding the project status. Note that these do not correspond to specific commits or milestones.

| Date     |  Status   |  Notes or observations   |
|----------|:-------------:|----------------------|
| June 13, 2025 |  active |  Added LlamaIndex tool listing for demonstration only. (The `--all-extras` flag is necessary to install LlamaIndex, which is not installed by default.) |
| June 9, 2025 |  active |  Added containerisation, support for self-signed, proxies. |
| June 8, 2025 |  active |  Added dynamic composition. |
| June 7, 2025 |  active |  Added tools to cover all the functionalities of the Frankfurter API. |
| June 7, 2025 |  active |  Project started.  |

## Installation

The directory where you clone this repository will be referred to as the _working directory_ or _WD_ hereinafter.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). To install the project with its minimal dependencies in a virtual environment, run the following in the _WD_. To install all non-essential dependencies (_which are required for developing and testing_), replace the `--no-dev` with the `--all-groups --all-extras` flag in the following command.

```bash
uv sync --no-dev
```

## Environment variables

Following is a list of environment variables that can be used to configure the application. A template of environment variables is provided in the file `.env.template`.

The following environment variables can be specified, prefixed with `FASTMCP_`: `HOST`, `PORT`, `DEBUG` and `LOG_LEVEL`. See [key configuration options](https://gofastmcp.com/servers/fastmcp#key-configuration-options) for FastMCP. Note that `on_duplicate_` prefixed options specified as environment variables _will be ignored_.

The underlying HTTP client also respects some environment variables, as documented in [the HTTPX library](https://www.python-httpx.org/environment_variables/). In addition, `SSL_CERT_FILE` and `SSL_CERT_DIR` can be configured to so that

| Variable |  [Default value] and description   |
|--------------|----------------|
| `HTTPX_TIMEOUT` | [5.0] The time for the underlying HTTP client to wait, in seconds, for a response. |
| `HTTPX_VERIFY_SSL` | [True] This variable can be set to False to turn off SSL certificate verification, if, for instance, you are using a proxy server with a self-signed certificate. However, setting this to False _is advised against_: instead, use the `SSL_CERT_FILE` and `SSL_CERT_DIR` variables to properly configure self-signed certificates. |
| `MCP_SERVER_TRANSPORT` | [streamable-http] The acceptable options are `stdio`, `sse` or `streamable-http`. Given the use-case of running this MCP server as a remotely accessible endpoint, there is no real reason to choose `stdio`. |
| `FRANKFURTER_API_URL` | [https://api.frankfurter.dev/v1] If you are [self-hosting the Frankfurter API](https://hub.docker.com/r/lineofflight/frankfurter), you should change this to the API endpoint address of your deployment. |

## Usage (with `pip`)

Add this package from PyPI using `pip` in a virtual environment (possibly managed by `conda` or `pyenv`) and then start the server by running the following.

Add a `.env` file with the contents of the `.env.template` file if you wish to modify the default values of the aforementioned environment variables. Or, on your shell, you can export the environment variables that you wish to modify.

```bash
pip install frankfurtermcp
python -m frankfurtermcp.server
```

## Usage (self-hosted server using `uv`)

Copy the `.env.template` file to a `.env` file in the _WD_, to modify the aforementioned environment variables, if you want to use anything other than the default settings. Or, on your shell, you can export the environment variables that you wish to modify.

Run the following in the _WD_ to start the MCP server.

```bash
uv run frankfurtermcp
```

If you want to run it without `uv`, assuming that the appropriate virtual environment has been created in the `.venv` within the _WD_, you can start the server calling the following.

```bash
./.venv/bin/python -m frankfurtermcp.server
```

The MCP endpoint will be available over HTTP at [http://localhost:8000/sse](http://localhost:8000/sse) for the Server Sent Events (SSE) transport, or [http://localhost:8000/mcp](http://localhost:8000/mcp) for the streamable HTTP transport. To exit the server, use the Ctrl+C key combination.

## Usage (self-hosted server using Docker)

There is one Dockerfile provided in this repository.

 - `local.dockerfile` for using the latest version, which can contain your edits to the code if you do make edits.

To build the image, create the container and start it, run the following in _WD_. _Choose shorter names for the image and container if you prefer._

If you change the port to anything other than 8000 in `.env.template`, _do remember to change the port number references in the following command_. Instead of passing all the environment variables using the `--env-file` option, you can also pass individual environment variables using the `-e` option.

```bash
docker build -f local.dockerfile -t frankfurtermcp .
docker create -p 8000:8000/tcp --env-file .env.template --expose 8000 --name frankfurtermcp-container frankfurtermcp
docker start frankfurtermcp-container
```

Upon successful build and container start, the MCP server will be available over HTTP at [http://localhost:8000/sse](http://localhost:8000/sse) for the Server Sent Events (SSE) transport, or [http://localhost:8000/mcp](http://localhost:8000/mcp) for the streamable HTTP transport.

## Usage (dynamic mounting with FastMCP)

To see how to use the MCP server by mounting it dynamically with [FastMCP](https://gofastmcp.com/), check the file [`src/frankfurtermcp/composition.py`](https://github.com/anirbanbasu/frankfurtermcp/blob/master/src/frankfurtermcp/composition.py).

## List of available tools

The following table lists the names of the tools as exposed by the FrankfurterMCP server. It does not list the tool(s) exposed through [the composition example](https://github.com/anirbanbasu/frankfurtermcp/blob/master/src/frankfurtermcp/composition.py). The descriptions shown here are for documentation purposes, which may differ from the actual descriptions exposed over the model context protocol.

| Name         |  Description   |
|--------------|----------------|
| `get_supported_currencies` | Get a list of currencies supported by the Frankfurter API. |
| `get_latest_exchange_rates` | Get latest exchange rates in specific currencies for a given base currency. |
| `convert_currency_latest` | Convert an amount from one currency to another using the latest exchange rates. |
| `get_historical_exchange_rates` | Get historical exchange rates for a specific date or date range in specific currencies for a given base currency. |
| `convert_currency_specific_date` | Convert an amount from one currency to another using the exchange rates for a specific date. |

The required and optional arguments for each tool are not listed in the following table for brevity but are available to the MCP client over the protocol.

If you want to see the detailed schema for a particular tool, you can do so using the `tools-info` commmand from the command line interface. The command line interface is available as the script `cli`. You can invoke its help to see the available commands as follows.

```bash
uv run cli --help
```

This will produce an output similar to the screenshot below.

![cli-help-screenshot](https://raw.githubusercontent.com/anirbanbasu/frankfurtermcp/master/screenshots/cli-help.png "FrankfurterMCP CLI help")

Before calling the `tools-info` command, you **MUST** have the server running in `streamable-http` or `sse` transport mode, preferably locally, e.g., by invoking `uv run frankfurtermcp`. A successful call of the `tools-info` command will generate an output similar to the screenshot shown below.

![cli-tools-info-screenshot](https://raw.githubusercontent.com/anirbanbasu/frankfurtermcp/master/screenshots/cli-tools-info.png "FrankfurterMCP CLI tools-info")

Alternative to the `tools-info` command, you can also run call the `llamaindex-tools-list` command to display the names of the tools without the respective function schemas. This functionality is provided only to optionally demonstrate that the LlamaIndex MCP client can read the tools list from this MCP server. In order for this to function, you must install LlamaIndex MCP client by calling `uv sync --extra opt`. The output of calling this command will look like the following.

![cli-llamaindex-tools-list-screenshot](https://raw.githubusercontent.com/anirbanbasu/frankfurtermcp/master/screenshots/cli-llamaindex-tools-list.png "FrankfurterMCP CLI llamaindex-tools-list")

## Contributing

Install [`pre-commit`](https://pre-commit.com/) for Git and [`ruff`](https://docs.astral.sh/ruff/installation/). Then enable `pre-commit` by running the following in the _WD_.

```bash
pre-commit install
```
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Testing

To run the provided test cases, execute the following. Add the flag `--capture=tee-sys` to the command to display further console output.

_Note that for the tests to succeed, the environment variable `MCP_SERVER_TRANSPORT` must be set to either `sse` or `streamable-http`, or not set at all, in which case it will default to `streamable-http`_.

```bash
uv run --group test pytest tests/
```

## License

[MIT](https://choosealicense.com/licenses/mit/).
