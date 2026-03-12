# Install minimal project dependencies in a virtual environment
install:
    @echo "Installing project dependencies in a virtual environment..."
    @uv sync --frozen --no-dev
    @echo "Project dependencies installed."

# Install all project dependencies in a virtual environment
install-all:
    @echo "Installing all project dependencies in a virtual environment..."
    @uv sync --frozen --all-groups
    @echo "All project dependencies installed."

# Install pre-commit hooks using 'prek'
install-pre-commit-hooks:
    @echo "Installing pre-commit hooks using prek..."
    @prek install
    @echo "Pre-commit hooks installed."

# Update pre-commit hooks using 'prek'
pre-commit-update:
    @echo "Updating pre-commit hooks using prek..."
    @prek auto-update
    @echo "Pre-commit hooks updated."

# Upgrade dependencies with releases older than a specified number of days (Unix version)
[unix]
upgrade-dependencies days="7":
    #!/usr/bin/env bash
    if [[ "$OSTYPE" == "darwin"* ]]; then
        D=$(date -v-{{ days }}d -u +%Y-%m-%d)
    else
        D=$(date -u -d "{{ days }} days ago" +%Y-%m-%d)
    fi
    echo "Upgrading dependencies with releases older than: $D"
    uv lock --upgrade --exclude-newer "$D"

# Upgrade dependencies with releases older than a specified number of days (Windows version)
[windows]
upgrade-dependencies days="7":
    @powershell -NoProfile -Command "$cutoff = (Get-Date).AddDays(-{{ days }}).ToString('yyyy-MM-dd'); Write-Host \"Upgrading dependencies with releases older than: $cutoff\"; uv lock --upgrade --exclude-newer $cutoff"

# Bump the patch version of the project using 'uv'
bump-patch:
    @echo "Updating current project version: $(uv version --short)"
    @uv version --bump patch
    @echo "Updated project to: $(uv version --short)"

# Format the code
format:
    @echo "Formatting code..."
    @uv run ruff format
    @uv run ruff check --fix --fix-only
    @echo "Code formatted."

# Run the type checker
type-check:
    @echo "Running type checker..."
    @uv run ty check
    @echo "Type checking complete."

export MCP_SERVER_TRANSPORT := "streamable-http"

# Run tests with coverage reporting
test-coverage:
    @echo "Running tests with coverage..."
    @uv run --group test coverage run -m pytest --capture=tee-sys -vvv --log-cli-level=INFO tests/
    @uv run coverage report -m
    @echo "Test coverage complete."

# Run the Open Source Vulnerability scanner
vulnerability-scan:
    @echo "Running Open Source Vulnerability scanner..."
    @osv-scanner scan source -r .
    @echo "Vulnerability scan complete."
