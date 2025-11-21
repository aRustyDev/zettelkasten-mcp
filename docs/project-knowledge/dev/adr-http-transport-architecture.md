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
