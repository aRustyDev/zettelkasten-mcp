# run uv tests
test:

# docker compose up
deploy:
    just -f docker/justfile deploy

# initialize the project for development
init: zed vscode

# initialize zed configs
[private]
zed:
    mv .zed/settings.json.example .zed/settings.json

# initialize vscode configs
[private]
vscode:
    mv .vscode/mcp.json.example .vscode/mcp.json
