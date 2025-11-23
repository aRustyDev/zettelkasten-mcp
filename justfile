# run all tests with coverage
test fmt="html" test="*":
    uv sync --extra dev
    uv run pytest "{{ if test == "*" { "tests" } else { "tests" / test } }}" -v --tb=short --cov=src --cov-report=term --cov-report="{{ fmt }}"

# run tests matching a keyword (usage: just test-match health)
test-match KEYWORD:
    uv run pytest tests/ -v --tb=short -k "{{ KEYWORD }}"

# docker compose up
deploy profile="prod": init
    just -f docker/justfile deploy "{{ profile }}"

# initialize the project for development
init: zed vscode

# initialize zed configs
[private]
zed:
    cat .zed/settings.json.example | envsubst > .zed/settings.json

# initialize vscode configs
[private]
vscode:
    cat .vscode/mcp.json.example | envsubst > .vscode/mcp.json
