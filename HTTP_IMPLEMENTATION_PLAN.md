# HTTP Transport Implementation Plan for Zettelkasten MCP

## Overview
This plan outlines the steps to add HTTP transport support to the zettelkasten-mcp server while maintaining backward compatibility with STDIO transport.

## Goals
- Add HTTP/SSE transport support using FastMCP's built-in capabilities
- Maintain backward compatibility with existing STDIO transport
- Make transport selection configurable via CLI arguments and environment variables
- Support both local development and production deployments
- Optional: Add CORS support for browser-based clients

## Prerequisites
- Existing codebase uses FastMCP from the MCP Python SDK
- Current implementation only supports STDIO transport
- Server architecture already separates concerns well

---

## Implementation Status

### ✅ Phase 1: Add Dependencies - COMPLETED
- **Date:** 2025-11-20
- **Status:** All dependencies added and verified
- **Git Commit:** d7f22f6 - "feat: Add HTTP transport dependencies"
- **Changes:**
  - Added `starlette>=0.27.0` to pyproject.toml (installed v0.46.1)
  - Added `uvicorn>=0.23.0` to pyproject.toml (installed v0.34.0)
  - Ran `uv sync` successfully (31 packages installed)
  - Verified server still starts and runs correctly
  - Verified new dependencies import correctly

### ✅ Phase 2: Update Configuration - COMPLETED
- **Date:** 2025-11-20
- **Status:** All configuration updates completed and verified
- **Git Commit:** 912dc36 - "feat: Add HTTP transport configuration"
- **Changes:**
  - Added HTTP configuration fields to `ZettelkastenConfig` in config.py:
    - `http_host` (default: 0.0.0.0)
    - `http_port` (default: 8000)
    - `http_cors_enabled` (default: false)
    - `http_cors_origins` (default: ["*"])
    - `json_response` (default: true)
  - Updated .env.example with HTTP configuration examples
  - Verified configuration loads correctly with default values
  - Verified environment variable overrides work correctly
  - Verified server still starts and runs without errors

### ✅ Phase 3: Update Server Implementation - COMPLETED
- **Date:** 2025-11-20
- **Status:** Server implementation updated to support HTTP transport
- **Git Commit:** b7b6265 - "feat: Implement HTTP transport in MCP server"
- **Changes:**
  - Modified FastMCP initialization to include `json_response=config.json_response`
  - Updated `run()` method with new signature:
    - Added `transport` parameter (default: "stdio")
    - Added `host` parameter (default: from config)
    - Added `port` parameter (default: from config)
    - Added `enable_cors` parameter (default: from config)
  - Implemented HTTP transport with FastMCP's streamable-http
  - Added optional CORS middleware support for browser clients
  - Lazy imports of starlette/uvicorn (only when HTTP is used)
  - Added detailed logging for each transport mode
  - Maintained backward compatibility - STDIO remains default
  - Verified server initialization and STDIO transport still work

### ✅ Phase 4: Update Entry Point - COMPLETED
- **Date:** 2025-11-20
- **Status:** Entry point updated with CLI argument support
- **Git Commit:** f657484 - "feat: Add CLI arguments for HTTP transport selection"
- **Changes:**
  - Updated `parse_args()` in main.py:
    - Added comprehensive help text with usage examples
    - Added `--transport` argument (choices: stdio, http, default: stdio)
    - Added `--host` argument for HTTP server host binding
    - Added `--port` argument for HTTP server port configuration
    - Added `--cors` flag to enable CORS middleware
    - Organized arguments into logical groups (storage, logging, transport)
  - Updated `main()` function to pass transport arguments to server.run()
  - Fixed HTTP transport implementation:
    - Changed from `streamable_http_app()` to `sse_app()` (correct FastMCP API)
    - Both CORS and non-CORS HTTP paths now use `uvicorn.run()` properly
  - Verified all transport modes work:
    - STDIO (default) ✓
    - HTTP on custom port ✓
    - HTTP with CORS enabled ✓
    - Environment variable overrides ✓

### ✅ Phase 5: Documentation Updates - COMPLETED
- **Date:** 2025-11-21
- **Status:** README updated with comprehensive transport documentation
- **Changes:**
  - Added "Transport Options" section to README.md:
    - STDIO Transport subsection with usage examples and Claude Desktop config
    - HTTP Transport subsection with usage examples and security warnings
    - Clear explanation of when to use each transport
  - Added "Command-Line Options" subsection to Usage section
  - Updated all command examples to use correct module path (zettelkasten_mcp.main)
  - Added security considerations for HTTP transport
  - Added environment variable configuration examples
  - Added Claude Code CLI integration instructions
  - Mentioned Server-Sent Events once for technical accuracy without emphasis
  - Verified all documented commands work correctly

### ⏳ Phase 6: Testing - PENDING

### ⏳ Phase 7: Docker Support - PENDING

---

## Phase 1: Add Dependencies

### Step 1.1: Update pyproject.toml
**File:** `pyproject.toml`

**Action:** Add HTTP server dependencies to the `dependencies` array:

```toml
dependencies = [
    "mcp[cli]>=1.2.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "markdown>=3.4.0",
    "python-frontmatter>=1.0.0",
    "python-dotenv>=1.0.0",
    # New HTTP dependencies
    "starlette>=0.27.0",
    "uvicorn>=0.23.0",
]
```

**Rationale:** Starlette provides the ASGI framework and uvicorn is the ASGI server needed for HTTP transport.

### Step 1.2: Install Dependencies
```bash
pip install -e .
# or if using uv
uv pip install -e .
```

---

## Phase 2: Update Configuration

### Step 2.1: Add HTTP Configuration to config.py
**File:** `src/zettelkasten_mcp/config.py`

**Action:** Add HTTP transport configuration parameters:

```python
# HTTP Transport Configuration
http_enabled: bool = os.getenv("ZETTELKASTEN_HTTP_ENABLED", "false").lower() == "true"
http_host: str = os.getenv("ZETTELKASTEN_HTTP_HOST", "0.0.0.0")
http_port: int = int(os.getenv("ZETTELKASTEN_HTTP_PORT", "8000"))
http_cors_enabled: bool = os.getenv("ZETTELKASTEN_HTTP_CORS", "false").lower() == "true"
http_cors_origins: list[str] = os.getenv("ZETTELKASTEN_HTTP_CORS_ORIGINS", "*").split(",")

# FastMCP HTTP settings
json_response: bool = os.getenv("ZETTELKASTEN_JSON_RESPONSE", "true").lower() == "true"
stateless_http: bool = os.getenv("ZETTELKASTEN_STATELESS_HTTP", "true").lower() == "true"
```

**Rationale:**
- Centralized configuration management
- Environment variable support for deployment flexibility
- Production-ready defaults (stateless, JSON responses)

### Step 2.2: Update .env.example
**File:** `.env.example`

**Action:** Add HTTP configuration examples:

```bash
# HTTP Transport Configuration (optional)
# ZETTELKASTEN_HTTP_ENABLED=false
# ZETTELKASTEN_HTTP_HOST=0.0.0.0
# ZETTELKASTEN_HTTP_PORT=8000
# ZETTELKASTEN_HTTP_CORS=false
# ZETTELKASTEN_HTTP_CORS_ORIGINS=*
# ZETTELKASTEN_JSON_RESPONSE=true
# ZETTELKASTEN_STATELESS_HTTP=true
```

---

## Phase 3: Update Server Implementation

### Step 3.1: Modify FastMCP Initialization
**File:** `src/zettelkasten_mcp/server/mcp_server.py`

**Current Code (approximate):**
```python
self.mcp = FastMCP(
    config.server_name,
    version=config.server_version
)
```

**Updated Code:**
```python
self.mcp = FastMCP(
    config.server_name,
    version=config.server_version,
    json_response=config.json_response,
)
```

**Rationale:** Enable JSON response mode for HTTP transport compatibility.

### Step 3.2: Update run() Method
**File:** `src/zettelkasten_mcp/server/mcp_server.py`

**Current Code:**
```python
def run(self) -> None:
    """Run the MCP server."""
    self.mcp.run()
```

**Updated Code:**
```python
def run(
    self,
    transport: str = "stdio",
    host: str | None = None,
    port: int | None = None,
    enable_cors: bool | None = None,
) -> None:
    """Run the MCP server.

    Args:
        transport: Transport type - "stdio" or "http"
        host: Host to bind to (for HTTP transport)
        port: Port to bind to (for HTTP transport)
        enable_cors: Enable CORS middleware (for HTTP transport)
    """
    # Use config defaults if not provided
    host = host or config.http_host
    port = port or config.http_port
    enable_cors = enable_cors if enable_cors is not None else config.http_cors_enabled

    if transport == "http":
        if enable_cors:
            # Import here to avoid dependency issues if not using HTTP
            from starlette.middleware.cors import CORSMiddleware
            import uvicorn

            app = CORSMiddleware(
                self.mcp.streamable_http_app(),
                allow_origins=config.http_cors_origins,
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["*"],
                expose_headers=["Mcp-Session-Id"],
            )

            uvicorn.run(app, host=host, port=port)
        else:
            self.mcp.run(transport="streamable-http", host=host, port=port)
    else:
        # Default STDIO transport
        self.mcp.run()
```

**Rationale:**
- Backward compatible - defaults to STDIO
- Flexible configuration via parameters or environment variables
- Optional CORS support for browser clients
- Lazy import of HTTP dependencies

---

## Phase 4: Update Entry Point

### Step 4.1: Modify main.py
**File:** `src/zettelkasten_mcp/main.py`

**Current Code (approximate):**
```python
def main() -> None:
    """Main entry point for the MCP server."""
    server = ZettelkastenMcpServer()
    server.run()
```

**Updated Code:**
```python
import argparse
from zettelkasten_mcp.server.mcp_server import ZettelkastenMcpServer
from zettelkasten_mcp import config


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description="Zettelkasten MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with STDIO (default, for Claude Desktop)
  python -m zettelkasten_mcp

  # Run with HTTP transport
  python -m zettelkasten_mcp --transport http

  # Run with HTTP on custom port
  python -m zettelkasten_mcp --transport http --port 8080

  # Run with HTTP and CORS enabled
  python -m zettelkasten_mcp --transport http --cors
        """
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help=f"HTTP host to bind to (default: {config.http_host})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=f"HTTP port to bind to (default: {config.http_port})",
    )
    parser.add_argument(
        "--cors",
        action="store_true",
        default=None,
        help="Enable CORS for HTTP transport (default: from config)",
    )

    args = parser.parse_args()

    server = ZettelkastenMcpServer()
    server.run(
        transport=args.transport,
        host=args.host,
        port=args.port,
        enable_cors=args.cors,
    )


if __name__ == "__main__":
    main()
```

**Rationale:**
- CLI argument parsing for transport selection
- Comprehensive help text with examples
- Falls back to config defaults when arguments not provided
- Maintains simple default behavior (STDIO)

---

## Phase 5: Documentation Updates

### Step 5.1: Update README.md
**File:** `README.md`

**Action:** Add HTTP transport section to the README:

**Section to Add (after existing Installation/Configuration):**

```markdown
## Transport Options

Zettelkasten MCP supports two transport mechanisms:

### STDIO Transport (Default)

For use with Claude Desktop or other local MCP clients:

```json
{
  "mcpServers": {
    "zettelkasten": {
      "command": "/path/to/zettelkasten-mcp/.venv/bin/python",
      "args": ["-m", "zettelkasten_mcp"],
      "env": {
        "ZETTELKASTEN_ROOT": "/path/to/your/zettelkasten"
      }
    }
  }
}
```

### HTTP Transport

For remote access or browser-based clients:

**Start the server:**
```bash
python -m zettelkasten_mcp --transport http --port 8000
```

**Configure Claude Code:**
```bash
claude mcp add --transport http zettelkasten http://localhost:8000/mcp
```

**Environment Variables:**
```bash
export ZETTELKASTEN_HTTP_HOST=0.0.0.0
export ZETTELKASTEN_HTTP_PORT=8000
export ZETTELKASTEN_HTTP_CORS=true
export ZETTELKASTEN_ROOT=/path/to/your/zettelkasten
python -m zettelkasten_mcp --transport http
```

**CORS Support:**
For browser-based clients, enable CORS:
```bash
python -m zettelkasten_mcp --transport http --cors
```

Or via environment:
```bash
export ZETTELKASTEN_HTTP_CORS=true
export ZETTELKASTEN_HTTP_CORS_ORIGINS=https://example.com,https://app.example.com
```
```

### Step 5.2: Create HTTP_USAGE.md (Optional)
Create a dedicated guide for HTTP deployment scenarios.

---

## Phase 6: Testing

### Step 6.1: Manual Testing Checklist

**STDIO Transport:**
- [ ] Server starts with default `python -m zettelkasten_mcp`
- [ ] Works with Claude Desktop configuration
- [ ] All existing tools/resources function correctly
- [ ] No regression in existing functionality

**HTTP Transport:**
- [ ] Server starts with `--transport http`
- [ ] Server binds to correct host/port
- [ ] Accepts HTTP requests at `/mcp` endpoint
- [ ] Returns proper JSON responses
- [ ] Can connect via `claude mcp add`

**CORS:**
- [ ] CORS headers present when `--cors` flag used
- [ ] `Mcp-Session-Id` header exposed
- [ ] OPTIONS requests handled correctly

**Configuration:**
- [ ] Environment variables override defaults
- [ ] CLI arguments override environment variables
- [ ] Config file values are respected

### Step 6.2: Automated Tests (Optional)

**File:** `tests/test_http_transport.py` (new file)

```python
import pytest
from zettelkasten_mcp.server.mcp_server import ZettelkastenMcpServer


def test_server_initialization():
    """Test that server initializes correctly."""
    server = ZettelkastenMcpServer()
    assert server is not None
    assert server.mcp is not None


def test_stdio_transport_default():
    """Test that STDIO is the default transport."""
    # This would require refactoring run() to be testable
    # or using subprocess to test the actual CLI
    pass


def test_http_transport_config():
    """Test HTTP transport configuration."""
    # Test that HTTP config is properly loaded
    pass
```

**Rationale:** Ensure reliability and prevent regressions.

---

## Phase 7: Docker Support (Optional)

### Step 7.1: Create HTTP-specific Dockerfile
**File:** `docker/Dockerfile.http`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml setup.py ./
COPY src/ ./src/

RUN pip install -e .

EXPOSE 8000

ENV ZETTELKASTEN_ROOT=/data
ENV ZETTELKASTEN_HTTP_HOST=0.0.0.0
ENV ZETTELKASTEN_HTTP_PORT=8000

CMD ["python", "-m", "zettelkasten_mcp", "--transport", "http"]
```

### Step 7.2: Create docker-compose.yml
**File:** `docker/docker-compose.http.yml`

```yaml
version: '3.8'

services:
  zettelkasten-mcp:
    build:
      context: ..
      dockerfile: docker/Dockerfile.http
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    environment:
      - ZETTELKASTEN_ROOT=/data
      - ZETTELKASTEN_HTTP_CORS=true
```

**Usage:**
```bash
docker-compose -f docker/docker-compose.http.yml up
```

---

## Implementation Order

1. **Phase 1:** Add dependencies (5 minutes)
2. **Phase 2:** Update configuration (10 minutes)
3. **Phase 3:** Update server implementation (20 minutes)
4. **Phase 4:** Update entry point (15 minutes)
5. **Phase 5:** Update documentation (15 minutes)
6. **Phase 6:** Testing (30 minutes)
7. **Phase 7:** Docker support - Optional (20 minutes)

**Total Estimated Time:** ~2 hours (excluding optional Docker phase)

---

## Rollout Strategy

### Option 1: Feature Branch
1. Create feature branch: `git checkout -b feature/http-transport`
2. Implement all phases
3. Test thoroughly
4. Create pull request
5. Merge to main after review

### Option 2: Incremental
1. Phase 1-2: Add dependencies and config
2. Phase 3-4: Implement HTTP transport
3. Phase 5: Documentation
4. Phase 6: Testing and refinement
5. Phase 7: Docker (separate PR)

---

## Verification Steps

After implementation, verify:

1. **STDIO still works:**
   ```bash
   python -m zettelkasten_mcp
   # Should start in STDIO mode
   ```

2. **HTTP works:**
   ```bash
   python -m zettelkasten_mcp --transport http
   # Should bind to port 8000
   ```

3. **Configuration works:**
   ```bash
   export ZETTELKASTEN_HTTP_PORT=9000
   python -m zettelkasten_mcp --transport http
   # Should bind to port 9000
   ```

4. **Claude Code integration:**
   ```bash
   claude mcp add --transport http zettelkasten http://localhost:8000/mcp
   # Should connect successfully
   ```

---

## Potential Issues and Solutions

### Issue 1: Port Already in Use
**Solution:** Make port configurable (already planned) and document how to change it.

### Issue 2: CORS Preflight Failures
**Solution:** Ensure proper CORS headers and OPTIONS handling (implemented in Phase 3).

### Issue 3: Session Management
**Solution:** Use `stateless_http=true` for production deployments.

### Issue 4: Authentication
**Future Enhancement:** Add API key or OAuth support if needed for production.

---

## Future Enhancements

1. **Authentication/Authorization**
   - API key support
   - OAuth integration
   - JWT tokens

2. **Monitoring/Observability**
   - Prometheus metrics endpoint
   - Health check endpoint
   - Request logging

3. **Rate Limiting**
   - Per-client rate limits
   - DDoS protection

4. **Load Balancing**
   - Multiple server instances
   - Session affinity

5. **WebSocket Support**
   - Real-time updates
   - Bi-directional streaming

---

## References

- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP HTTP Transport Guide](https://modelcontextprotocol.io/docs/tools/http-servers)
- [Starlette Documentation](https://www.starlette.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

---

## Notes

- FastMCP's built-in HTTP support makes this implementation straightforward
- Backward compatibility is maintained - existing STDIO usage is unaffected
- Production deployments should use `stateless_http=true` for scalability
- CORS should only be enabled when necessary (browser clients)
