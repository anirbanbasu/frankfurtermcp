[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=3776ab&labelColor=e4e4e4)](https://www.python.org/downloads/release/python-3120/) [![pytest](https://github.com/anirbanbasu/frankfurtermcp/actions/workflows/uv-pytest.yml/badge.svg)](https://github.com/anirbanbasu/frankfurtermcp/actions/workflows/uv-pytest.yml) ![GitHub commits since latest release](https://img.shields.io/github/commits-since/anirbanbasu/frankfurtermcp/latest)
 [![PyPI](https://img.shields.io/pypi/v/frankfurtermcp?label=pypi%20package)](https://pypi.org/project/frankfurtermcp/#history)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/frankfurtermcp?label=pypi%20downloads)](https://pypi.org/project/frankfurtermcp/)
[![Verified on MseeP](https://mseep.ai/badge.svg)](https://mseep.ai/app/c6527bdb-9b60-430d-9ed6-cb3c8b9a2b54) [![smithery badge](https://smithery.ai/badge/@anirbanbasu/frankfurtermcp)](https://smithery.ai/server/@anirbanbasu/frankfurtermcp)

# Frankfurter MCP

[Frankfurter](https://frankfurter.dev/) is a useful API for latest currency exchange rates, historical data, or time series published by sources such as the European Central Bank. Should you have to access the Frankfurter API as tools for language model agents exposed over the Model Context Protocol (MCP), Frankfurter MCP is what you need.

# Installation

_If your objective is to use the tools available on this MCP server, please refer to the usage > client sub-section below_.

The directory where you clone this repository will be referred to as the _working directory_ or _WD_ hereinafter.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). To install the project with its minimal dependencies in a virtual environment, run the following in the _WD_. To install all non-essential dependencies (_which are required for developing and testing_), replace the `--no-dev` with the `--all-groups` flag in the following command.

```bash
uv sync --no-dev
```

## Environment variables

Following is a list of environment variables that can be used to configure the application. A template of environment variables is provided in the file `.env.template`. _Note that the default values listed in the table below are not always the same as those in the `.env.template` file_.

The following environment variables can be specified, prefixed with `FASTMCP_`: `HOST`, `PORT`, `DEBUG` and `LOG_LEVEL`. See [global configuration options](https://gofastmcp.com/servers/server#global-settings) for FastMCP. Note that `on_duplicate_` prefixed options specified as environment variables _will be ignored_.

The underlying HTTP client also respects some environment variables, as documented in [the HTTPX library](https://www.python-httpx.org/environment_variables/). In addition, `SSL_CERT_FILE` and `SSL_CERT_DIR` can be configured to use self-signed certificates of hosted API endpoint or intermediate HTTP(S) proxy server(s).

| Variable |  [Default value] and description   |
|--------------|----------------|
| `LOG_LEVEL` | [INFO] The level for logging. Changing this level also affects the log output of other dependent libraries that may use the same environment variable. See valid values at [Python logging documentation](https://docs.python.org/3/library/logging.html#logging-levels). |
| `HTTPX_TIMEOUT` | [5.0] The time for the underlying HTTP client to wait, in seconds, for a response from the Frankfurter API. |
| `HTTPX_VERIFY_SSL` | [True] This variable can be set to False to turn off SSL certificate verification, if, for instance, you are using a proxy server with a self-signed certificate. However, setting this to False _is advised against_: instead, use the `SSL_CERT_FILE` and `SSL_CERT_DIR` variables to properly configure self-signed certificates. |
| `FAST_MCP_HOST` | [localhost] This variable specifies which host the MCP server must bind to unless the server transport (see below) is set to `stdio`. |
| `FAST_MCP_PORT` | [8000] This variable specifies which port the MCP server must listen on unless the server transport (see below) is set to `stdio`. |
| `MCP_SERVER_TRANSPORT` | [stdio] The acceptable options are `stdio`, `sse` or `streamable-http`. However, in the `.env.template`, the default value is set to `stdio`. |
| `MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE` | [True] This specifies if additional metadata will be included with the MCP type `TextContent` that wraps the response data from each tool call. The additional metadata, for example, will include the API URL of the Frankfurter server, amongst others, that is used to obtain the responses. |
| `FRANKFURTER_API_URL` | [https://api.frankfurter.dev/v1] If you are [self-hosting the Frankfurter API](https://hub.docker.com/r/lineofflight/frankfurter), you should change this to the API endpoint address of your deployment. |

# Usage

The following sub-sections illustrate how to run the Frankfurter MCP as a server and how to access it from MCP clients.

## Server
While running the server, you have the choice to use `stdio` transport or HTTP options (`sse` or the newer `streamable-http`).

Using default settings and `MCP_SERVER_TRANSPORT` set to `sse` or `streamable-http`, the MCP endpoint will be available over HTTP at [http://localhost:8000/sse](http://localhost:8000/sse) for the Server Sent Events (SSE) transport, or [http://localhost:8000/mcp](http://localhost:8000/mcp) for the streamable HTTP transport.

If you want to run Frankfurter MCP with `stdio` transport and the default parameters, execute the commands below without using the `.env.template` file.

### Server with `uv`

_Optional_: Copy the `.env.template` file to a `.env` file in the _WD_, to modify the aforementioned environment variables, if you want to use anything other than the default settings. Or, on your shell, you can export the environment variables that you wish to modify.

Run the following in the _WD_ to start the MCP server.

```bash
uv run frankfurtermcp
```

### Server with `pip` from PyPI package

Add this package from PyPI using `pip` in a virtual environment (possibly managed by `uv`, `pyenv` or `conda`) and then start the server by running the following.

_Optional_: Add a `.env` file with the contents of the `.env.template` file if you wish to modify the default values of the aforementioned environment variables. Or, on your shell, you can export the environment variables that you wish to modify.

```bash
pip install frankfurtermcp
python -m frankfurtermcp.server
```

### Server using Docker

There are two Dockerfiles provided in this repository.

 - `local.dockerfile` for containerising the Frankfurter MCP server.
 - `smithery.dockerfile` for deploying to [Smithery AI](https://smithery.ai/), which you do not have to use.

To build the image, create the container and start it, run the following in _WD_. _Choose shorter names for the image and container if you prefer._

If you change the port to anything other than 8000 in `.env.template`, _do remember to change the port number references in the following command_. Instead of passing all the environment variables using the `--env-file` option, you can also pass individual environment variables using the `-e` option.

```bash
docker build -t frankfurtermcp -f local.dockerfile .
docker create -p 8000:8000/tcp --env-file .env.template --expose 8000 --name frankfurtermcp-container frankfurtermcp
docker start frankfurtermcp-container
```

Upon successful build and container start, the MCP server will be available over HTTP at [http://localhost:8000/sse](http://localhost:8000/sse) for the Server Sent Events (SSE) transport, or [http://localhost:8000/mcp](http://localhost:8000/mcp) for the streamable HTTP transport.

### Cloud hosted servers

The currently available cloud hosted options are as follows.

 - FastMCP Cloud: https://frankfurtermcp.fastmcp.app/mcp
 - Glama.AI: https://glama.ai/mcp/servers/@anirbanbasu/frankfurtermcp
 - Smithery.AI: https://smithery.ai/server/@anirbanbasu/frankfurtermcp


## Client access

This sub-section explains ways for a client to connect and test the FrankfurterMCP server.

### The official MCP visual inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is an _official_ Model Context Protocol tool that can be used by developers to test and debug MCP servers. This is the most comprehensive way to explore the MCP server.

To use it, you must have Node.js installed. The best way to install and manage `node` as well as packages such as the MCP Inspector is to use the [Node Version Manager (or, `nvm`)](https://github.com/nvm-sh/nvm). Once you have `nvm` installed, you can install and use the latest Long Term Release version of `node` by executing the following.

```bash
nvm install --lts
nvm use --lts
```

Following that (install and) run the MCP Inspector by executing the following in the _WD_.

```bash
npx @modelcontextprotocol/inspector uv run frankfurtermcp
```

This will create a local URL at port 6274 with an authentication token, which you can copy and browse to on your browser. Once on the MCP Inspector UI, press _Connect_ to connect to the MCP server. Thereafter, you can explore the tools available on the server.

### Claude Desktop, Visual Studio, and so on

The server entry to run with `stdio` transport that you can use with systems such as Claude Desktop, Visual Studio Code, and so on is as follows.

```json
{
    "command": "uv",
    "args": [
        "run",
        "frankfurtermcp"
    ]
}
```

Instead of having `frankfurtermcp` as the last item in the list of `args`, you may need to specify the full path to the script, e.g., _WD_`/.venv/bin/frankfurtermcp`. Likewise, instead of using `uv`, you could also have the following JSON configuration with the path properly substituted for `python3.12`, for instance such as _WD_`/.venv/bin/python3.12`.

```json
{
    "command": "python3.12",
    "args": [
        "-m",
        "frankfurtermcp.server"
    ]
}
```

# List of available MCP features

FrankfurterMCP has the following MCP features.

## Tools

The following table lists the names of the tools as exposed by the FrankfurterMCP server. The descriptions shown here are for documentation purposes, which may differ from the actual descriptions exposed over the model context protocol.

| Name         |  Description   |
|--------------|----------------|
| `get_supported_currencies` | Get a list of currencies supported by the Frankfurter API. |
| `get_latest_exchange_rates` | Get latest exchange rates in specific currencies for a given base currency. |
| `convert_currency_latest` | Convert an amount from one currency to another using the latest exchange rates. |
| `get_historical_exchange_rates` | Get historical exchange rates for a specific date or date range in specific currencies for a given base currency. |
| `convert_currency_specific_date` | Convert an amount from one currency to another using the exchange rates for a specific date. |

The required and optional arguments for each tool are not listed in the following table for brevity but are available to the MCP client over the protocol.

# Contributing

Install [`pre-commit`](https://pre-commit.com/) for Git and [`ruff`](https://docs.astral.sh/ruff/installation/). Then enable `pre-commit` by running the following in the _WD_.

```bash
pre-commit install
```
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

# Testing and coverage

To run the provided test cases, execute the following. Add the flag `--capture=tee-sys` to the command to display further console output.

```bash
uv run --group test pytest tests/
```

There is a handy testing script _WD_`/run-tests.sh`, which will run all the tests and generate a coverage report as follows. It can also accept arguments and parameters to be passed to `pytest`, such as `-k` for filtering the tests to run. If all tests are run, the generated coverage report may look like the one below.

```bash
Name                             Stmts   Miss  Cover
----------------------------------------------------
src/frankfurtermcp/__init__.py      10      0   100%
src/frankfurtermcp/common.py        23      0   100%
src/frankfurtermcp/mixin.py         52      4    92%
src/frankfurtermcp/model.py         17      0   100%
src/frankfurtermcp/server.py       111     20    82%
tests/__init__.py                    0      0   100%
tests/test_data_models.py           60      0   100%
tests/test_server.py                71      0   100%
----------------------------------------------------
TOTAL                              344     24    93%
```

# License

[MIT](https://choosealicense.com/licenses/mit/).

# Project status

Following is a table of some updates regarding the project status. Note that these do not correspond to specific commits or milestones.

| Date     |  Status   |  Notes or observations   |
|----------|:-------------:|----------------------|
| September 6, 2025 |  active |  Code refactoring and cleanup. |
| June 27, 2025 |  active |  Successful remote deployments on Glama.AI and Smithery.AI. |
| June 9, 2025 |  active |  Added containerisation, support for self-signed proxies. |
| June 7, 2025 |  active |  Project started. Added tools to cover all the functionalities of the Frankfurter API. |
