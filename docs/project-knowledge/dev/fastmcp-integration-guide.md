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
