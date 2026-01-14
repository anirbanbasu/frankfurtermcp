[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=3776ab&labelColor=e4e4e4)](https://www.python.org/downloads/release/python-3120/) [![pytest](https://github.com/anirbanbasu/frankfurtermcp/actions/workflows/uv-pytest-coverage.yml/badge.svg)](https://github.com/anirbanbasu/frankfurtermcp/actions/workflows/uv-pytest-coverage.yml) ![GitHub commits since latest release](https://img.shields.io/github/commits-since/anirbanbasu/frankfurtermcp/latest)
 [![PyPI](https://img.shields.io/pypi/v/frankfurtermcp?label=pypi%20package)](https://pypi.org/project/frankfurtermcp/#history)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/frankfurtermcp?label=pypi%20downloads)](https://pypi.org/project/frankfurtermcp/)
[![Verified on MseeP](https://mseep.ai/badge.svg)](https://mseep.ai/app/c6527bdb-9b60-430d-9ed6-cb3c8b9a2b54) [![smithery badge](https://smithery.ai/badge/@anirbanbasu/frankfurtermcp)](https://smithery.ai/server/@anirbanbasu/frankfurtermcp)

# Frankfurter MCP

[Frankfurter](https://frankfurter.dev/) is a useful API for latest currency exchange rates, historical data, or time series published by sources such as the European Central Bank. Should you have to access the Frankfurter API as tools for language model agents exposed over the Model Context Protocol (MCP), Frankfurter MCP is what you need.

# Installation

_If your objective is to use the tools available on this MCP server, please refer to the usage > client sub-section below_.

The directory where you clone this repository will be referred to as the _working directory_ or _WD_ hereinafter.

Install [just](https://just.systems/man/en/) to manage project tasks.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). To install the project with its minimal dependencies in a virtual environment, run the `just install` in the _WD_. To install all non-essential dependencies (_which are required for developing and testing_), run `just install-all` instead.

## Environment variables

Following is a list of environment variables that can be used to configure the application. A template of environment variables is provided in the file `.env.template`. _Note that the default values listed in the table below are not always the same as those in the `.env.template` file_.

The following environment variables can be specified, prefixed with `FASTMCP_`: `HOST`, `PORT`, `DEBUG` and `LOG_LEVEL`. See [global configuration options](https://gofastmcp.com/servers/server#global-settings) for FastMCP. Note that `on_duplicate_` prefixed options specified as environment variables _will be ignored_.

The underlying HTTP client also respects some environment variables, as documented in [the HTTPX library](https://www.python-httpx.org/environment_variables/). In addition, `SSL_CERT_FILE` and `SSL_CERT_DIR` can be configured to use self-signed certificates of hosted API endpoint or intermediate HTTP(S) proxy server(s).

Frankfurter MCP will cache calls to the Frankfurter API to improve performance. The cache happens with two different strategies. For API calls whose responses do not change for certain parameters, e.g., historical rate lookup, a least recently used (LRU) cache is used. For API calls whose responses do change, e.g., latest rate lookup, a time-to-live (TTL) cache is used with a default time-to-live set to 15 minutes. The cache parameters can be adjusted using the environment variables, see below.

| Variable |  [Default value] and description   |
|--------------|----------------|
| `LOG_LEVEL` | [INFO] The level for logging. Changing this level also affects the log output of other dependent libraries that may use the same environment variable. See valid values at [Python logging documentation](https://docs.python.org/3/library/logging.html#logging-levels). |
| `HTTPX_TIMEOUT` | [5.0] The time for the underlying HTTP client to wait, in seconds, for a response from the Frankfurter API. |
| `HTTPX_VERIFY_SSL` | [True] This variable can be set to False to turn off SSL certificate verification, if, for instance, you are using a proxy server with a self-signed certificate. However, setting this to False _is advised against_: instead, use the `SSL_CERT_FILE` and `SSL_CERT_DIR` variables to properly configure self-signed certificates. |
| `FAST_MCP_HOST` | [localhost] This variable specifies which host the MCP server must bind to unless the server transport (see below) is set to `stdio`. _Note that running the server to bind to any IP by specifying `0.0.0.0` poses a security threat. Such a setting should only be used in demo environments._|
| `FAST_MCP_PORT` | [8000] This variable specifies which port the MCP server must listen on unless the server transport (see below) is set to `stdio`. |
| `CORS_MIDDLEWARE_ALLOW_ORIGINS` | ["localhost", "127.0.0.1"] This variable specifies [Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS) allowed origins for the MCP server unless the server transport (see below) is set to `stdio`. You **must** set it to "*" explicitly (and you will get a warning by doing so) if you want to test this server over an HTTP transport using [the MCP inspector described below](https://github.com/anirbanbasu/frankfurtermcp?tab=readme-ov-file#the-official-mcp-visual-inspector). |
| `MCP_SERVER_TRANSPORT` | [stdio] The acceptable options are `stdio`, `sse` or `streamable-http`. However, in the `.env.template`, the default value is set to `stdio`. |
| `MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE` | [True] This specifies if additional metadata will be included with the MCP  response from each tool call. The additional metadata, for example, will include the API URL of the Frankfurter server, amongst others, that is used to obtain the responses. |
| `FRANKFURTER_API_URL` | [https://api.frankfurter.dev/v1] If you are [self-hosting the Frankfurter API](https://hub.docker.com/r/lineofflight/frankfurter), you should change this to the API endpoint address of your deployment. |
| `LRU_CACHE_MAX_SIZE` | [1024] The maximum size of the least recently used (LRU) cache for API calls. |
| `TTL_CACHE_MAX_SIZE` | [256] The maximum size of the time-to-live (TTL) cache for API calls. |
| `TTL_CACHE_TTL_SECONDS` | [900] The time limit, in seconds, of the time-to-live (TTL) cache for API calls. |
| `UVICORN_LIMIT_CONCURRENCY` | [100] The maximum number of concurrent connections the server will accept. This helps prevent resource exhaustion from too many simultaneous connections. Only applies when using HTTP transports (`sse` or `streamable-http`). |
| `UVICORN_LIMIT_MAX_REQUESTS` | [10000] The maximum number of requests a worker will process before being restarted. This helps prevent memory leaks from accumulating over time. Only applies when using HTTP transports (`sse` or `streamable-http`). |
| `UVICORN_TIMEOUT_KEEP_ALIVE` | [60] The timeout in seconds for keeping idle connections alive. Idle connections will be closed after this period to free up resources. Only applies when using HTTP transports (`sse` or `streamable-http`). |
| `UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN` | [5] The timeout in seconds for graceful shutdown. The server will wait this long for active connections to complete before forcefully shutting down. Only applies when using HTTP transports (`sse` or `streamable-http`). |
| `RATE_LIMIT_MAX_REQUESTS_PER_SECOND` | [10.0] The maximum number of requests allowed per second using a token bucket algorithm. This implements rate limiting to prevent API abuse and ensure fair resource allocation. |
| `RATE_LIMIT_BURST_CAPACITY` | [20] The burst capacity for the rate limiter, allowing short bursts of requests above the per-second limit. This provides flexibility for legitimate usage patterns while still protecting against sustained high request rates. |
| `REQUEST_SIZE_LIMIT_BYTES` | [102400] The maximum size in bytes for HTTP request bodies (default 100KB). Requests exceeding this limit will be rejected with a 413 status code. This prevents memory exhaustion attacks from large payloads. Only applies when using HTTP transports (`sse` or `streamable-http`). |
| `DOCKER_TMPFS_SIZE_MB` | [100] The size in megabytes for the temporary filesystem (`/tmp`) when running in Docker with read-only root filesystem. This temporary storage is used for runtime file operations. Increase this value if the application requires more temporary storage for caching or processing large datasets. Only relevant when deploying with Docker Compose. |

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
 - `smithery.dockerfile` for deploying to [Smithery AI](https://smithery.ai/), which you do not have to use. Note that runtime hardening of the container based on this Dockerfile is not provided in this repository through Docker Compose because this is managed by Smithery AI during deployment.

First, make a copy of the `.env.template` to a `.env` file. Then, modify the following variables in the `.env` file as needed.

 - `FASTMCP_HOST`: Set to `0.0.0.0` to allow external access to the container. _This is only for local testing and is not recommended for production deployments_.
 - `CORS_MIDDLEWARE_ALLOW_ORIGINS`: Set to `*` to allow external access to the MCP server from any origin. _This is needed if you want to test the server using the MCP Inspector over HTTP transport and is not recommended for production deployments_.

To build the image, create the container and start it using Docker Compose, run the following in _WD_.

If you change the port to anything other than 8000 in `.env`, _do remember to change the port number in `docker-compose.yml`_. Instead of using the `.env` file, you can also modify `docker-compose.yml` to pass individual environment variables using the `environment` section.

```bash
docker compose up --build
```

To run in detached mode (background), add the `-d` flag:

```bash
docker compose up -d --build
```

To stop the container:

```bash
docker compose down
```

The `docker-compose.yml` file includes security hardening with read-only filesystem, dropped capabilities, seccomp and AppArmor profiles, and resource limits (512MB memory, 1 CPU).

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
| `greet` | Get a greeting from the FrankfurterMCP server. _This is mostly used for internal testing_. |

The required and optional arguments for each tool are not listed in the following table for brevity but are available to the MCP client over the protocol.

# Contributing

Install [`prek`](https://prek.j178.dev/). Then enable `prek` by running the following in the _WD_.

```bash
prek install
```
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

# Testing and coverage

To run the provided test cases, execute the following. Add the flag `--capture=tee-sys` to the command to display further console output.

```bash
uv run --group test pytest tests/
```

Invoke `just test-coverage` to run all the tests and generate a coverage report as follows. If all tests are run, the generated coverage report may look like the one below.

```bash
---------------------------------------------------------------------------------------- benchmark: 2 tests ---------------------------------------------------------------------------------------
Name (time in ms)                         Min               Max              Mean            StdDev            Median               IQR            Outliers       OPS            Rounds  Iterations
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_get_historical_exchange_rates     4.4944 (1.0)      5.1512 (1.0)      4.7919 (1.0)      0.2460 (1.0)      4.7819 (1.0)      0.3249 (1.0)           2;0  208.6840 (1.0)           5           1
test_get_latest_exchange_rates         4.7937 (1.07)     5.6976 (1.11)     5.3257 (1.11)     0.3345 (1.36)     5.4182 (1.13)     0.3575 (1.10)          2;0  187.7702 (0.90)          5           1
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
=============================================================== 15 passed in 4.09s ===============================================================
Name    Stmts   Miss    Cover   Missing
---------------------------------------
TOTAL     244      0  100.00%

6 files skipped due to complete coverage.
Test coverage complete.
```

# License

[MIT](https://choosealicense.com/licenses/mit/).

# Project status

Following is a table of some updates regarding the project status. Note that these do not correspond to specific commits or milestones.

| Date     |  Status   |  Notes or observations   |
|----------|:-------------:|----------------------|
| December 2, 2025 |  active |  Added a middleware to remove unknown tool arguments, such as [those passed by `n8n`](https://github.com/n8n-io/n8n/issues/21500). |
| November 26, 2025 |  active |  Using the new [`ToolResult` to package response metadata](https://gofastmcp.com/servers/tools#toolresult-and-metadata). |
| November 21, 2025 |  active |  New tooling using `prek` (instead of `pre-commit`), `ty` (instead of `mypy`) and `just`. |
| September 6, 2025 |  active |  Code refactoring and cleanup. |
| June 27, 2025 |  active |  Successful remote deployments on Glama.AI and Smithery.AI. |
| June 9, 2025 |  active |  Added containerisation, support for self-signed proxies. |
| June 7, 2025 |  active |  Project started. Added tools to cover all the functionalities of the Frankfurter API. |
