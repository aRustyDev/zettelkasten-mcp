# Zettelkasten MCP Server

A Model Context Protocol (MCP) server that implements the Zettelkasten knowledge management methodology, allowing you to create, link, explore and synthesize atomic notes through Claude and other MCP-compatible clients.

## What is Zettelkasten?

The Zettelkasten method is a knowledge management system developed by German sociologist Niklas Luhmann, who used it to produce over 70 books and hundreds of articles. It consists of three core principles:

1. **Atomicity**: Each note contains exactly one idea, making it a discrete unit of knowledge
2. **Connectivity**: Notes are linked together to create a network of knowledge, with meaningful relationships between ideas
3. **Emergence**: As the network grows, new patterns and insights emerge that weren't obvious when the individual notes were created

What makes the Zettelkasten approach powerful is how it enables exploration in multiple ways:

- **Vertical exploration**: dive deeper into specific topics by following connections within a subject area.
- **Horizontal exploration**: discover unexpected relationships between different fields by traversing links that cross domains.

This structure invites serendipitous discoveries as you follow trails of thought from note to note, all while keeping each piece of information easily accessible through its unique identifier. Luhmann called his system his "second brain" or "communication partner" - this digital implementation aims to provide similar benefits through modern technology.

## Features

- Create atomic notes with unique timestamp-based IDs
- Link notes bidirectionally to build a knowledge graph
- Tag notes for categorical organization
- Search notes by content, tags, or links
- Use markdown format for human readability and editing
- Integrate with Claude through MCP for AI-assisted knowledge management
- Dual storage architecture (see below)
- Synchronous operation model for simplified architecture

## Examples

- Knowledge creation: [A small Zettelkasten knowledge network about the Zettelkasten method itself](https://github.com/entanglr/zettelkasten-mcp/discussions/5)

## Note Types

The Zettelkasten MCP server supports different types of notes:

|Type|Handle|Description|
|---|---|---|
|**Fleeting notes**|`fleeting`|Quick, temporary notes for capturing ideas|
|**Literature notes**|`literature`|Notes from reading material|
|**Permanent notes**|`permanent`|Well-formulated, evergreen notes|
|**Structure notes**|`structure`|Index or outline notes that organize other notes|
|**Hub notes**|`hub`|Entry points to the Zettelkasten on key topics|

## Link Types

The Zettelkasten MCP server uses a comprehensive semantic linking system that creates meaningful connections between notes. Each link type represents a specific relationship, allowing for a rich, multi-dimensional knowledge graph.

| Primary Link Type | Inverse Link Type | Relationship Description |
|-------------------|-------------------|--------------------------|
| `reference` | `reference` | Simple reference to related information (symmetric relationship) |
| `extends` | `extended_by` | One note builds upon or develops concepts from another |
| `refines` | `refined_by` | One note clarifies or improves upon another |
| `contradicts` | `contradicted_by` | One note presents opposing views to another |
| `questions` | `questioned_by` | One note poses questions about another |
| `supports` | `supported_by` | One note provides evidence for another |
| `related` | `related` | Generic relationship (symmetric relationship) |

## Prompting

To ensure maximum effectiveness, we recommend using a system prompt ("project instructions"), project knowledge, and an appropriate chat prompt when asking the LLM to process information, or explore or synthesize your Zettelkasten notes. The `docs` directory in this repository contains the necessary files to get you started:

### System prompts

Pick one:

- [system-prompt.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/prompts/system/system-prompt.md)
- [system-prompt-with-protocol.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/prompts/system/system-prompt-with-protocol.md)

### Project knowledge

For end users:

- [zettelkasten-methodology-technical.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/project-knowledge/user/zettelkasten-methodology-technical.md)
- [link-types-in-zettelkasten-mcp-server.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/project-knowledge/user/link-types-in-zettelkasten-mcp-server.md)
- (more info relevant to your project)

### Chat Prompts

- [chat-prompt-knowledge-creation.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/prompts/chat/chat-prompt-knowledge-creation.md)
- [chat-prompt-knowledge-creation-batch.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/prompts/chat/chat-prompt-knowledge-creation-batch.md)
- [chat-prompt-knowledge-exploration.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/prompts/chat/chat-prompt-knowledge-exploration.md)
- [chat-prompt-knowledge-synthesis.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/prompts/chat/chat-prompt-knowledge-synthesis.md)

### Project knowledge (dev)

For developers and contributors:

- [Example - A simple MCP server.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/project-knowledge/dev/Example%20-%20A%20simple%20MCP%20server%20that%20exposes%20a%20website%20fetching%20tool.md)
- [MCP Python SDK-README.md](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/project-knowledge/dev/MCP%20Python%20SDK-README.md)
- [llms-full.txt](https://github.com/entanglr/zettelkasten-mcp/blob/main/docs/project-knowledge/dev/llms-full.txt)

NB: Optionally include the source code with a tool like [repomix](https://github.com/yamadashy/repomix).

## Storage Architecture

This system uses a dual storage approach:

1. **Markdown Files**: All notes are stored as human-readable Markdown files with YAML frontmatter for metadata. These files are the **source of truth** and can be:
   - Edited directly in any text editor
   - Placed under version control (Git, etc.)
   - Backed up using standard file backup procedures
   - Shared or transferred like any other text files

2. **SQLite Database**: Functions as an indexing layer that:
   - Facilitates efficient querying and search operations
   - Enables Claude to quickly traverse the knowledge graph
   - Maintains relationship information for faster link traversal
   - Is automatically rebuilt from Markdown files when needed

If you edit Markdown files directly outside the system, you'll need to run the `zk_rebuild_index` tool to update the database. The database itself can be deleted at any time - it will be regenerated from your Markdown files.

## Installation

```bash
# Clone the repository
git clone https://github.com/entanglr/zettelkasten-mcp.git
cd zettelkasten-mcp

# Create a virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv add "mcp[cli]"

# Install dev dependencies
uv sync --all-extras
```

## Configuration

Create a `.env` file in the project root by copying the example:

```bash
cp .env.example .env
```

Then edit the file to configure your connection parameters.

## Transport Options

The Zettelkasten MCP server supports two transport mechanisms for different use cases:

### STDIO Transport (Default)

STDIO (Standard Input/Output) transport is the default mode, designed for local MCP clients like Claude Desktop. The server communicates through standard input and output streams, making it ideal for:

- **Claude Desktop integration**: Direct integration with Claude Desktop application
- **Local development**: Running the server on your local machine
- **Simple setup**: No network configuration required
- **Security**: No network exposure, everything runs locally

**Usage:**

```bash
# Run with default STDIO transport
python -m zettelkasten_mcp.main
```

**Claude Desktop Configuration:**

Add this to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "zettelkasten": {
      "command": "/absolute/path/to/zettelkasten-mcp/.venv/bin/python",
      "args": ["-m", "zettelkasten_mcp.main"],
      "env": {
        "ZETTELKASTEN_NOTES_DIR": "/absolute/path/to/data/notes",
        "ZETTELKASTEN_DATABASE_PATH": "/absolute/path/to/data/db/zettelkasten.db"
      }
    }
  }
}
```

### HTTP Transport (Streamable HTTP)

HTTP transport using Modern Streamable HTTP enables remote access to the MCP server. This is useful for:

- **Remote access**: Connect to the server from different machines
- **Editor integration**: Connect from Zed, VS Code, or other MCP-compatible editors
- **Development**: Testing with tools like Claude Code CLI or mcp-remote
- **Team collaboration**: Share a single server instance (with appropriate security measures)

**Endpoint:** `http://localhost:8000/mcp` (unified endpoint for all operations)
**Health Check:** `http://localhost:8000/health`

**Basic Usage:**

```bash
# Start HTTP server on default port (8000)
python -m zettelkasten_mcp.main --transport http

# Start on custom port
python -m zettelkasten_mcp.main --transport http --port 9000

# Start with custom host and port
python -m zettelkasten_mcp.main --transport http --host 0.0.0.0 --port 8080
```

**Connecting from Zed Editor:**

Add to your Zed settings (`~/.config/zed/settings.json`):

```json
{
  "context_servers": {
    "zettelkasten": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Connecting with mcp-remote:**

```bash
# Interactive MCP client
npx mcp-remote http://localhost:8000/mcp
```

**With CORS (for browser-based clients):**

```bash
# Enable CORS for browser access
python -m zettelkasten_mcp.main --transport http --cors

# Or via environment variable
export ZETTELKASTEN_HTTP_CORS=true
python -m zettelkasten_mcp.main --transport http
```

**Claude Code CLI Configuration:**

```bash
# Add HTTP server to Claude Code
claude mcp add --transport http zettelkasten http://localhost:8000/mcp
```

**Environment Variables:**

```bash
# HTTP server configuration
export ZETTELKASTEN_HTTP_HOST=0.0.0.0
export ZETTELKASTEN_HTTP_PORT=8000
export ZETTELKASTEN_HTTP_CORS=true
export ZETTELKASTEN_HTTP_CORS_ORIGINS="https://example.com,https://app.example.com"

# Run with environment configuration
python -m zettelkasten_mcp.main --transport http
```

**Security Considerations:**

⚠️ **Important**: When running HTTP transport:
- The server has no built-in authentication - use a reverse proxy (nginx, Apache) for production
- Enable CORS only when necessary and specify allowed origins
- Consider using HTTPS via a reverse proxy for encrypted connections
- Restrict network access using firewalls when appropriate
- The HTTP transport is best suited for development or trusted network environments

## Docker Deployment

For containerized deployments with HTTP transport, Docker support is available:

### Quick Start with Docker Compose

```bash
# Clone the repository
git clone https://github.com/entanglr/zettelkasten-mcp.git
cd zettelkasten-mcp

# Start the HTTP server
docker-compose -f docker/docker-compose.http.yml up -d

# The server will be available at http://localhost:8000
```

### Docker Compose Configuration

The docker-compose setup provides:
- Automatic container management
- Persistent data volumes for notes and database
- Health checks for reliability
- Easy configuration via environment variables

**Basic deployment:**
```bash
# Start in foreground (see logs)
docker-compose -f docker/docker-compose.http.yml up

# Start in background (detached mode)
docker-compose -f docker/docker-compose.http.yml up -d

# View logs
docker-compose -f docker/docker-compose.http.yml logs -f

# Stop the server
docker-compose -f docker/docker-compose.http.yml down
```

**Custom configuration:**

Create a `.env` file in the `docker/` directory:
```bash
# Copy the example
cp docker/.env.example docker/.env

# Edit with your settings
ZETTELKASTEN_HTTP_PORT=9000
ZETTELKASTEN_HTTP_CORS=true
ZETTELKASTEN_LOG_LEVEL=DEBUG
```

Then start the server:
```bash
docker-compose -f docker/docker-compose.http.yml up
```

### Building the Docker Image

To build the HTTP transport Docker image manually:

```bash
# Build the image
docker build -f docker/Dockerfile.http -t zettelkasten-mcp:http .

# Run the container
docker run -d \
  -p 8000:8000 \
  -v ./data/notes:/var/data/notes \
  -v ./data/db:/var/data/db \
  -e ZETTELKASTEN_HTTP_CORS=true \
  --name zettelkasten-mcp \
  zettelkasten-mcp:http
```

### Docker Environment Variables

All configuration can be controlled via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ZETTELKASTEN_NOTES_DIR` | `/var/data/notes` | Directory for note storage |
| `ZETTELKASTEN_DATABASE_PATH` | `/var/data/db/zettelkasten.db` | SQLite database path |
| `ZETTELKASTEN_HTTP_HOST` | `0.0.0.0` | HTTP server bind address |
| `ZETTELKASTEN_HTTP_PORT` | `8000` | HTTP server port |
| `ZETTELKASTEN_HTTP_CORS` | `false` | Enable CORS |
| `ZETTELKASTEN_HTTP_CORS_ORIGINS` | `*` | Allowed CORS origins |
| `ZETTELKASTEN_LOG_LEVEL` | `INFO` | Logging level |

### Production Deployment

For production deployments, consider:

1. **Use a reverse proxy** (nginx, Traefik, Caddy) for:
   - HTTPS/TLS termination
   - Authentication
   - Rate limiting
   - Request logging

2. **Data persistence**: Mount volumes to ensure data survives container restarts:
   ```yaml
   volumes:
     - /path/to/persistent/notes:/var/data/notes
     - /path/to/persistent/db:/var/data/db
   ```

3. **Resource limits**: Set memory and CPU limits in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 512M
   ```

4. **Monitoring**: Use health checks and monitoring tools:
   ```bash
   # Check container health
   docker ps

   # View resource usage
   docker stats zettelkasten-mcp-http
   ```

## Usage

### Command-Line Options

```bash
python -m zettelkasten_mcp.main --help
```

**Available arguments:**

- `--transport {stdio,http}`: Transport type (default: stdio)
- `--host HOST`: HTTP server host (default: 0.0.0.0)
- `--port PORT`: HTTP server port (default: 8000)
- `--cors`: Enable CORS for HTTP transport
- `--notes-dir DIR`: Directory for note storage
- `--database-path PATH`: SQLite database file path
- `--log-level LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Starting the Server

**STDIO mode (default, for Claude Desktop):**

```bash
python -m zettelkasten_mcp.main
```

**HTTP mode (for remote access):**

```bash
python -m zettelkasten_mcp.main --transport http --port 8000
```

**With explicit configuration:**

```bash
python -m zettelkasten_mcp.main \
  --transport stdio \
  --notes-dir ./data/notes \
  --database-path ./data/db/zettelkasten.db \
  --log-level INFO
```

See the [Transport Options](#transport-options) section above for detailed configuration instructions for both STDIO and HTTP transports.

## Available MCP Tools

All tools have been prefixed with `zk_` for better organization:

| Tool | Description |
|---|---|
| `zk_create_note` | Create a new note with a title, content, and optional tags |
| `zk_get_note` | Retrieve a specific note by ID or title |
| `zk_update_note` | Update an existing note's content or metadata |
| `zk_delete_note` | Delete a note |
| `zk_create_link` | Create links between notes |
| `zk_remove_link` | Remove links between notes |
| `zk_search_notes` | Search for notes by content, tags, or links |
| `zk_get_linked_notes` | Find notes linked to a specific note |
| `zk_get_all_tags` | List all tags in the system |
| `zk_find_similar_notes` | Find notes similar to a given note |
| `zk_find_central_notes` | Find notes with the most connections |
| `zk_find_orphaned_notes` | Find notes with no connections |
| `zk_list_notes_by_date` | List notes by creation/update date |
| `zk_rebuild_index` | Rebuild the database index from Markdown files |

## Project Structure

```
zettelkasten-mcp/
├── src/
│   └── zettelkasten_mcp/
│       ├── models/       # Data models
│       ├── storage/      # Storage layer
│       ├── services/     # Business logic
│       └── server/       # MCP server implementation
├── data/
│   ├── notes/            # Note storage (Markdown files)
│   └── db/               # Database for indexing
├── tests/                # Test suite
├── .env.example          # Environment variable template
└── README.md
```

## Tests

Comprehensive test suite for Zettelkasten MCP covering all layers of the application from models to the MCP server implementation.

### How to Run the Tests

From the project root directory, run:

#### Using pytest directly
```bash
python -m pytest -v tests/
```

#### Using UV
```bash
uv run pytest -v tests/
```

#### With coverage report
```bash
uv run pytest --cov=zettelkasten_mcp --cov-report=term-missing tests/
```

#### Running a specific test file
```bash
uv run pytest -v tests/test_models.py
```

#### Running a specific test class
```bash
uv run pytest -v tests/test_models.py::TestNoteModel
```

#### Running a specific test function
```bash
uv run pytest -v tests/test_models.py::TestNoteModel::test_note_validation
```

### Tests Directory Structure

```
tests/
├── conftest.py - Common fixtures for all tests
├── test_integration.py - Integration tests for the entire system
├── test_mcp_server.py - Tests for MCP server tools
├── test_models.py - Tests for data models
├── test_note_repository.py - Tests for note repository
├── test_search_service.py - Tests for search service
├── test_semantic_links.py - Tests for semantic linking
└── test_zettel_service.py - Tests for zettel service
```

## Important Notice

**⚠️ USE AT YOUR OWN RISK**: This software is experimental and provided as-is without warranty of any kind. While efforts have been made to ensure data integrity, it may contain bugs that could potentially lead to data loss or corruption. Always back up your notes regularly and use caution when testing with important information.

## Credit Where Credit's Due

This MCP server was crafted with the assistance of Claude, who helped organize the atomic thoughts of this project into a coherent knowledge graph. Much like a good Zettelkasten system, Claude connected the dots between ideas that might otherwise have remained isolated. Unlike Luhmann's paper-based system, however, Claude didn't require 90,000 index cards to be effective.

## License

MIT License
