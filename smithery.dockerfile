# Smithery does not work with base images such as ghcr.io/astral-sh/uv:python3.12-bookworm-slim
FROM python:3.12-alpine3.22
# Install system dependencies
RUN apk add --no-cache gcc musl-dev linux-headers
# Create a non-root user.
RUN adduser app_user
# Switch to the non-root user
USER app_user
# Set the working directory in the container
WORKDIR /home/app_user/app

COPY src pyproject.toml README.md LICENSE ./
# Install the latest version from the cloned repository
RUN pip install --upgrade pip && pip install --no-cache-dir .

ENV PATH="/home/app_user/.local/bin:$PATH"

# For stdio transport, we need a direct entrypoint
ENTRYPOINT ["python3", "-m", "frankfurtermcp.server"]
