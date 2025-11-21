# HTTP Transport Implementation - Phase 10: Developer Documentation

**Status:** ✅ COMPLETED
**Date:** 2025-11-21
**Commit:** (pending)
**Plan:** [Back to main plan](../HTTP_IMPLEMENTATION.md)

---


### Overview
Document architectural decisions, implementation details, and technical context for future developers working on the HTTP transport feature or extending the codebase.

### Step 10.1: Create HTTP Transport Architecture ADR
**File:** `docs/project-knowledge/dev/adr-http-transport-architecture.md`

**Content:**
```markdown
# ADR: HTTP Transport Architecture

## Status
Accepted - Implemented in Phase 1-8

## Context
The zettelkasten-mcp server originally supported only STDIO transport for local Claude Desktop usage. Users requested HTTP transport support for remote access and browser-based clients.

## Decision
Implement HTTP transport using FastMCP's built-in `sse_app()` method with Server-Sent Events (SSE) for the MCP protocol over HTTP.

## Rationale
1. **FastMCP Built-in Support**: FastMCP already provides `sse_app()` for HTTP transport
2. **SSE Standard**: Server-Sent Events is the standard MCP-over-HTTP protocol
3. **Backward Compatibility**: STDIO remains default, HTTP is opt-in
4. **Minimal Dependencies**: Only adds starlette and uvicorn
5. **Production Ready**: Supports stateless HTTP for scalability

## Consequences
### Positive
- Remote access capability without SSH tunneling
- Browser-based client support with CORS
- Docker deployment for production
- Configuration flexibility (CLI, env vars, config file)

### Negative
- Additional dependencies (starlette, uvicorn)
- No built-in authentication (must use reverse proxy)
- Slightly more complex configuration

## Alternatives Considered
1. **Custom HTTP Implementation**: Rejected - reinventing the wheel
2. **WebSocket Transport**: Rejected - FastMCP doesn't support it natively
3. **gRPC Transport**: Rejected - not MCP standard

## Implementation Notes
- Uses `sse_app()` not `streamable_http_app()` (which doesn't exist)
- Lazy imports HTTP dependencies only when needed
- Optional CORS middleware for browser clients
- Configuration precedence: CLI > ENV > Config defaults
```

### Step 10.2: Create Lazy Loading ADR
**File:** `docs/project-knowledge/dev/adr-lazy-loading-http-dependencies.md`

**Content:**
```markdown
# ADR: Lazy Loading HTTP Dependencies

## Status
Accepted - Implemented in Phase 3

## Context
HTTP dependencies (uvicorn, starlette) are only needed when running in HTTP mode, not for default STDIO usage. We want to avoid importing unnecessary modules for STDIO users.

## Decision
Import HTTP dependencies inside the `run()` method only when `transport == "http"`:

```python
if transport == "http":
    import uvicorn  # Lazy import
    if enable_cors:
        from starlette.middleware.cors import CORSMiddleware  # Lazy import
```

## Rationale
1. **Faster Startup**: STDIO mode doesn't import HTTP modules
2. **Smaller Memory Footprint**: No unused modules loaded
3. **Optional Dependencies**: Could make HTTP deps optional in future
4. **Clear Separation**: HTTP code only runs when explicitly requested

## Consequences
### Positive
- STDIO startup remains fast and lightweight
- Clear dependency boundaries
- Easy to make HTTP optional in future

### Negative
- Slightly more complex testing (can't patch at module level)
- Import errors only caught at runtime when HTTP is used

## Testing Implications
Because imports are dynamic, standard mocking patterns fail:
```python
# This FAILS - uvicorn not at module level
@patch('zettelkasten_mcp.server.mcp_server.uvicorn')
def test_http_transport(mock_uvicorn):
    ...
```

Solutions:
1. Patch `sys.modules['uvicorn']` before calling run()
2. Patch `builtins.__import__`
3. Refactor to inject uvicorn dependency

See `http-transport-test-improvements.md` for details.
```

### Step 10.3: Create Configuration Pattern ADR
**File:** `docs/project-knowledge/dev/adr-pydantic-config-pattern.md`

**Content:**
```markdown
# ADR: Pydantic Configuration with Environment Variables

## Status
Accepted - Implemented in Phase 2

## Context
Need centralized configuration for HTTP transport with support for environment variables, sensible defaults, and type safety.

## Decision
Use Pydantic BaseModel with Field defaults that read from environment variables:

```python
class ZettelkastenConfig(BaseModel):
    http_host: str = Field(
        default=os.getenv("ZETTELKASTEN_HTTP_HOST", "0.0.0.0")
    )
    http_port: int = Field(
        default=int(os.getenv("ZETTELKASTEN_HTTP_PORT", "8000"))
    )
```

## Rationale
1. **Type Safety**: Pydantic validates types automatically
2. **Environment Variables**: Reads from env with fallback defaults
3. **Single Source of Truth**: All config in one place
4. **Self-Documenting**: Field definitions show defaults and types

## Consequences
### Positive
- Type-safe configuration
- Environment variable support
- Clear defaults
- Validation built-in

### Negative
- Field defaults evaluate at module load time (not instance creation)
- Cannot override env vars in tests after module import
- Must reload module to change env var behavior in tests

## Testing Implications
Pydantic evaluates `Field(default=os.getenv(...))` when the module is first imported. Setting environment variables in tests after import has no effect:

```python
# This pattern FAILS
def test_http_port_from_env(monkeypatch):
    monkeypatch.setenv("ZETTELKASTEN_HTTP_PORT", "9000")
    config = ZettelkastenConfig()  # Already evaluated default at module load
    assert config.http_port == 9000  # FAILS - still 8000
```

Solutions:
1. Use `default_factory=lambda: os.getenv(...)` instead of `default=os.getenv(...)`
2. Reload config module in tests: `importlib.reload(config)`
3. Test environment variable behavior through integration tests

See `http-transport-test-improvements.md` for details.
```

### Step 10.4: Create FastMCP Integration Guide
**File:** `docs/project-knowledge/dev/fastmcp-integration-guide.md`

**Content:**
```markdown
# FastMCP Integration Guide

## Overview
This document explains how zettelkasten-mcp integrates with FastMCP for both STDIO and HTTP transports.

## FastMCP Initialization
```python
self.mcp = FastMCP(
    config.server_name,
    version=config.server_version,
    json_response=config.json_response,  # Required for HTTP transport
)
```

### json_response Parameter
- **Purpose**: Enables JSON-formatted responses for HTTP clients
- **Default**: `true` (from config)
- **Required for**: HTTP transport with SSE
- **Works with**: Both STDIO and HTTP transports

## STDIO Transport
Default transport for local Claude Desktop usage:

```python
self.mcp.run()  # Simple - no arguments needed
```

### When to Use
- Claude Desktop integration
- Local development
- Direct process communication

## HTTP Transport
For remote access and browser-based clients:

```python
app = self.mcp.sse_app()  # Get ASGI app
uvicorn.run(app, host=host, port=port)  # Run with uvicorn
```

### Key Methods
- `sse_app()`: Returns ASGI app for Server-Sent Events transport
- **NOT** `streamable_http_app()`: This method doesn't exist (common mistake)

### When to Use
- Remote server deployments
- Browser-based clients
- Docker containerization
- Multi-user access

## CORS Middleware
Optional for browser-based clients:

```python
from starlette.middleware.cors import CORSMiddleware

app = CORSMiddleware(
    self.mcp.sse_app(),
    allow_origins=config.http_cors_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],  # Required for MCP
)

uvicorn.run(app, host=host, port=port)
```

### CORS Headers
- `Mcp-Session-Id`: Must be exposed for MCP protocol
- `allow_origins`: Configure based on deployment (default: ["*"])
- `allow_methods`: GET, POST, OPTIONS for MCP
- `allow_headers`: Wildcard for flexibility

## Common Pitfalls

### 1. Wrong Method Name
```python
# WRONG - This method doesn't exist
app = self.mcp.streamable_http_app()

# CORRECT
app = self.mcp.sse_app()
```

### 2. Missing json_response
```python
# WRONG - HTTP won't work without json_response
self.mcp = FastMCP(config.server_name, version=config.server_version)

# CORRECT
self.mcp = FastMCP(
    config.server_name,
    version=config.server_version,
    json_response=True
)
```

### 3. Forgetting Mcp-Session-Id Header
```python
# WRONG - Browser clients won't work
app = CORSMiddleware(
    self.mcp.sse_app(),
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    # Missing expose_headers!
)

# CORRECT
app = CORSMiddleware(
    self.mcp.sse_app(),
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],  # Required!
)
```

## Testing FastMCP Integration

### Unit Tests
Mock the FastMCP instance:
```python
with patch.object(server.mcp, 'run') as mock_run:
    server.run(transport="stdio")
    mock_run.assert_called_once()
```

### Integration Tests
Use actual HTTP requests:
```python
import requests
# Start server in background thread
response = requests.get(f"http://localhost:{port}/health")
assert response.status_code == 200
```

## References
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://modelcontextprotocol.io/docs/tools/fastmcp)
- [Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html)
```

### Step 10.5: Update Test Improvements Documentation
**File:** `docs/project-knowledge/dev/http-transport-test-improvements.md`

**Action:** Add reference to the new ADR documents at the top

**Content to add at beginning:**
```markdown
> **Note**: For architectural context on why these testing challenges exist, see:
> - [ADR: Lazy Loading HTTP Dependencies](adr-lazy-loading-http-dependencies.md)
> - [ADR: Pydantic Configuration Pattern](adr-pydantic-config-pattern.md)

---
```

---

