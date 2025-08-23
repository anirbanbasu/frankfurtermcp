# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12.5-slim-bookworm

WORKDIR /app

COPY --from=uv --chown=app:app /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# ARG FASTMCP_HOST="0.0.0.0"
# ARG MCP_SERVER_TRANSPORT="streamable-http"

# RUN echo "MCP_SERVER_TRANSPORT=${MCP_SERVER_TRANSPORT}" > /app/.env && echo "FASTMCP_HOST=${FASTMCP_HOST}" >> /app/.env

# Set the correct environment variables as required by Smithery proxy
# EXPOSE ${PORT}

# See how PORT is obtained dynamically: https://github.com/anirbanbasu/frankfurtermcp/issues/26#issuecomment-3213947048
ENTRYPOINT ["sh", "-c", "MCP_SERVER_TRANSPORT=streamable-http FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=${PORT:-8080} python3 -m frankfurtermcp.server"]
# CMD ["MCP_SERVER_TRANSPORT=streamable-http FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=${PORT:-8081} python3 -m frankfurtermcp.server"]
