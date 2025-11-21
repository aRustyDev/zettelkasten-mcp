# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- HTTP transport support for the MCP server (in progress)
  - Added starlette and uvicorn dependencies for HTTP/SSE transport
  - Added HTTP configuration options to support both STDIO and HTTP transports
  - Configuration options for HTTP host, port, CORS, and JSON response mode
  - Environment variable support for all HTTP settings
- CHANGELOG.md to track project changes
- HTTP_IMPLEMENTATION_PLAN.md documenting the HTTP transport implementation roadmap

### Changed
- Updated `pyproject.toml` to include HTTP transport dependencies:
  - Added `starlette>=0.27.0` (v0.46.1 installed)
  - Added `uvicorn>=0.23.0` (v0.34.0 installed)
- Updated `config.py` with HTTP transport configuration fields:
  - `http_host` - Host address for HTTP server (default: 0.0.0.0)
  - `http_port` - Port for HTTP server (default: 8000)
  - `http_cors_enabled` - Enable CORS middleware (default: false)
  - `http_cors_origins` - Allowed CORS origins (default: ["*"])
  - `json_response` - Enable JSON response mode for FastMCP (default: true)
- Updated `.env.example` with HTTP configuration examples
- Updated `server/mcp_server.py` to support HTTP transport:
  - Modified FastMCP initialization to enable JSON response mode
  - Updated `run()` method to accept transport, host, port, and CORS parameters
  - Implemented HTTP transport using FastMCP's SSE (Server-Sent Events) API
  - Added optional CORS middleware support for browser-based clients
  - Lazy imports of HTTP dependencies (only loaded when needed)
  - Added detailed logging for transport modes
  - Maintained backward compatibility with STDIO transport
- Updated `main.py` entry point with CLI argument support:
  - Added `--transport` flag to choose between stdio and http
  - Added `--host`, `--port`, and `--cors` flags for HTTP configuration
  - Added comprehensive help text with usage examples
  - All transport configuration falls back to environment variables or defaults

### Technical Details

#### Phase 1: Dependencies (Completed 2025-11-20)
- Commit: d7f22f6
- Added HTTP server dependencies to support remote access
- All dependencies installed and verified working
- Backward compatible with existing STDIO transport

#### Phase 2: Configuration (Completed 2025-11-20)
- Commit: 912dc36
- Added Pydantic configuration fields for HTTP transport
- All configuration values use environment variables with sensible defaults
- Verified configuration loading and environment variable overrides
- Server continues to work with existing STDIO functionality

#### Phase 3: Server Implementation (Completed 2025-11-20)
- Commit: b7b6265
- Updated MCP server to support both STDIO and HTTP transports
- HTTP transport uses FastMCP's built-in SSE (Server-Sent Events) API
- Optional CORS middleware for browser clients
- Lazy loading of HTTP dependencies (starlette/uvicorn)
- Default behavior unchanged - STDIO transport remains the default
- All changes are backward compatible

#### Phase 4: Entry Point (Completed 2025-11-20)
- Commit: f657484
- Added CLI argument parsing for transport selection
- Users can now run: `python -m zettelkasten_mcp --transport http --port 8000`
- Comprehensive help text with examples for all transport modes
- Fixed HTTP transport implementation to use correct FastMCP SSE API
- Verified all transport modes: STDIO (default), HTTP, HTTP with CORS
- Falls back to environment variables and config defaults

## [1.2.1] - Previous Release

### Features
- STDIO-based MCP server for Zettelkasten knowledge management
- SQLite database for note storage
- Markdown-based note format with frontmatter support
- Note creation, retrieval, updating, and deletion
- Tag-based organization
- Link management between notes

---

## Implementation Status

### Completed Phases
- ✅ Phase 1: Add Dependencies
- ✅ Phase 2: Update Configuration
- ✅ Phase 3: Update Server Implementation
- ✅ Phase 4: Update Entry Point

### In Progress
- 🔄 Phase 5: Documentation Updates

### Planned
- ⏳ Phase 6: Testing
- ⏳ Phase 7: Docker Support (Optional)

---

## Migration Guide

### For Existing Users
No action required. The server continues to work with STDIO transport by default. All HTTP-related features are opt-in and disabled by default.

### To Enable HTTP Transport
HTTP transport is now available! Run the server with:

```bash
python -m zettelkasten_mcp --transport http --port 8000
```

Or via environment variables:
```bash
export ZETTELKASTEN_HTTP_PORT=8000
python -m zettelkasten_mcp --transport http
```

---

[Unreleased]: https://github.com/entanglr/zettelkasten-mcp/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/entanglr/zettelkasten-mcp/releases/tag/v1.2.1
