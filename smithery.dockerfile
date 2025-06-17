# Smithery does not work with base images such as ghcr.io/astral-sh/uv:python3.12-bookworm-slim
FROM python:3.12.5-slim-bookworm

# Create a non-root user.
RUN useradd -m -u 1000 app_user

# Switch to the non-root user
USER app_user
# Set the working directory in the container
WORKDIR /home/app_user/app

COPY ./README.md ./LICENSE ./pyproject.toml .env.smithery ./src ./
RUN mv .env.smithery .env

RUN pip install --upgrade pip && pip install --no-cache-dir .

ENV PATH="/home/app_user/.local/bin:$PATH"

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["MCP_SERVER_TRANSPORT=stdio frankfurtermcp"]
