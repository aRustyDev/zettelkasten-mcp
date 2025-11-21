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

## Health Check Endpoint

For Docker/Kubernetes deployments, a health check endpoint is available at `/health`:

```python
async def health_check(request):
    """Health check endpoint for Docker/Kubernetes monitoring."""
    from starlette.responses import JSONResponse

    return JSONResponse({
        "status": "healthy",
        "service": "zettelkasten-mcp",
        "transport": "http"
    })

def create_app_with_health(mcp_app):
    """Wrap MCP SSE app with health check endpoint."""
    from starlette.routing import Route, Mount
    from starlette.applications import Starlette

    return Starlette(
        routes=[
            Route("/health", health_check, methods=["GET"]),
            Mount("/", app=mcp_app),
        ]
    )
```

### Usage
```python
# Wrap the MCP app with health check
base_app = self.mcp.sse_app()
app = create_app_with_health(base_app)

# Apply CORS if needed
if enable_cors:
    from starlette.middleware.cors import CORSMiddleware
    app = CORSMiddleware(app, ...)

# Run the server
uvicorn.run(app, host=host, port=port)
```

### Response Format
```json
{
  "status": "healthy",
  "service": "zettelkasten-mcp",
  "transport": "http"
}
```

### Docker Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1
```

### Kubernetes Probes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 3
  periodSeconds: 10
```

### Implementation Details
- Health check uses Starlette routing to wrap FastMCP's SSE app
- `/health` endpoint is intercepted before MCP app
- All other requests are passed to MCP app at root path
- Minimal overhead - only processes `/health` requests
- Works with and without CORS middleware

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
