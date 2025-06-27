# Smithery does not work with base images such as ghcr.io/astral-sh/uv:python3.12-bookworm-slim
FROM python:3.12.5-slim-bookworm
# Create a non-root user.
RUN useradd -m -u 1000 app_user
# Switch to the non-root user
USER app_user
# Set the working directory in the container
WORKDIR /home/app_user/
COPY src/ pyproject.toml README.md LICENSE ./
# Install the latest version from the cloned repository
RUN pip install --upgrade pip && pip install --no-cache-dir .

ENV PATH="/home/app_user/.local/bin:$PATH"

# For stdio transport, we need a direct entrypoint
ENTRYPOINT ["python3", "-m", "frankfurtermcp.server"]
