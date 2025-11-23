---
id: F628B564-5D2F-4A64-A658-4FDA04E2256D
title: "Phase 3: Code Updates for Streamable HTTP"
status: ✅ Completed
date: 2025-11-22
author: aRustyDev
related:
  - 2F7850D8-3E51-456C-AE60-C70BAF323BFB  # Plan: Streamable HTTP Implementation
  - 4F557F9D-D5A9-4ACD-88D2-C741353CAC20  # Phase 2: Upgrade Dependencies
---

# Phase 3: Code Updates for Streamable HTTP

**Duration:** 1-2 hours
**Status:** ⏸️ Pending

---

## Objective

Update codebase to use Modern Streamable HTTP transport instead of Legacy HTTP+SSE.

---

## Tasks

### 3.1 Update MCP Server Initialization

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/src/zettelkasten_mcp/server/mcp_server.py`

**Change:**
```diff
 class ZettelkastenMcpServer:
     """MCP server for Zettelkasten."""
     def __init__(self):
         """Initialize the MCP server."""
         self.mcp = FastMCP(
             config.server_name,
             version=config.server_version,
             json_response=config.json_response,
+            stateless_http=True,  # Optimize for Streamable HTTP
         )
```

**Why `stateless_http=True`?**
- **Recommended** for Streamable HTTP deployments
- Each HTTP request gets a fresh transport instance
- Better for **load balancing** and **horizontal scaling**
- Matches Zed's expected stateless behavior
- No server-side session state to manage

**Performance Impact:**
- ✅ **Better:** Horizontal scaling, no memory leaks from long sessions
- ⚠️ **Trade-off:** Slightly higher overhead per request (negligible for our use case)

---

### 3.2 Update Config Class

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/src/zettelkasten_mcp/config.py`

**First, check current config:**
```bash
# Review existing HTTP config
grep -A 5 "http_host\|http_port" src/zettelkasten_mcp/config.py
```

**Add new fields:**
```python
class Config(BaseSettings):
    # ... existing fields ...

    # HTTP Transport Settings
    http_host: str = "0.0.0.0"
    http_port: int = 8000
    stateless_http: bool = True  # NEW: Enable stateless HTTP mode
    streamable_http_path: str = "/mcp"  # NEW: Streamable HTTP endpoint path

    # ... rest of config ...
```

**Purpose:**
- `stateless_http`: Controls transport behavior (aligns with FastMCP init)
- `streamable_http_path`: Makes endpoint path configurable (currently `/mcp`)

---

### 3.3 Update Main Entry Point

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/src/zettelkasten_mcp/__main__.py`

**Change transport initialization:**
```diff
 async def main():
     """Run the MCP server."""
     mcp_server = ZettelkastenMcpServer()

     if transport == "stdio":
         await mcp_server.mcp.run_async(transport="stdio")
     elif transport == "http":
-        # Legacy HTTP+SSE transport
+        # Modern Streamable HTTP transport
         from zettelkasten_mcp.server.mcp_server import create_app_with_health
-        sse_app = mcp_server.mcp.sse_app(
-            sse_path="/sse",
-            message_path="/messages/"
+
+        # Create Streamable HTTP app
+        http_app = mcp_server.mcp.http_app(
+            path="/mcp",  # Single unified endpoint
+            transport="streamable-http",
+            json_response=config.json_response,
+            stateless_http=config.stateless_http,
         )
-        app = create_app_with_health(sse_app)
+
+        # Wrap with health check
+        app = create_app_with_health(http_app)
+
         import uvicorn
         logger.info(f"Starting HTTP server on {config.http_host}:{config.http_port}")
         uvicorn.run(
             app,
             host=config.http_host,
             port=config.http_port,
             log_level=config.log_level.lower(),
         )
     else:
         raise ValueError(f"Unknown transport: {transport}")
```

**Key Changes:**
1. **Old:** `sse_app()` with separate `/sse` and `/messages/` endpoints
2. **New:** `http_app()` with unified `/mcp` endpoint
3. **Transport:** Explicitly specify `"streamable-http"`

**What `http_app()` does:**
- Creates Starlette ASGI app with Streamable HTTP support
- Mounts single `/mcp` endpoint handling GET/POST/DELETE
- Implements session management via `Mcp-Session-Id` header
- Returns proper 202 Accepted responses for POST requests

---

### 3.4 Update Health Check Endpoint

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/src/zettelkasten_mcp/server/mcp_server.py`

**Update transport name in health response:**
```diff
 async def health_check(request):
     """Health check endpoint for Docker/Kubernetes monitoring."""
     from starlette.responses import JSONResponse

     return JSONResponse({
         "status": "healthy",
         "service": "zettelkasten-mcp",
-        "transport": "http"
+        "transport": "streamable-http"  # Reflect new transport type
     })
```

**Purpose:**
- Monitoring tools can see we're using Streamable HTTP
- Helps with debugging if clients connect to wrong endpoint
- Documents the protocol version we support

---

### 3.5 Verify No Hardcoded SSE References

```bash
# Search for SSE-specific code that needs updating
cd /Users/arustydev/repos/mcp/zettelkasten-mcp

grep -r "sse_app\|/sse\|/messages" src/ --include="*.py"
grep -r "text/event-stream" src/ --include="*.py"
```

**Expected:** Should only find matches in comments or logging (not active code)

**If Found:**
- Review each occurrence
- Replace with Streamable HTTP equivalents
- Document changes

---

## Deliverables

After completing this phase, you should have:

- ✅ MCP server initialization updated with `stateless_http=True`
- ✅ Config class has `stateless_http` and `streamable_http_path` fields
- ✅ Main entry point uses `http_app()` instead of `sse_app()`
- ✅ Endpoint changed from `/sse` + `/messages/` to `/mcp`
- ✅ Health check reflects `"transport": "streamable-http"`
- ✅ No lingering SSE-specific code references

---

## Verification Checklist

Before proceeding to Phase 4:

- [ ] `mcp_server.py` has `stateless_http=True` in FastMCP init
- [ ] `config.py` has new `stateless_http` and `streamable_http_path` fields
- [ ] `__main__.py` uses `http_app()` with `transport="streamable-http"`
- [ ] Health endpoint returns `"transport": "streamable-http"`
- [ ] Code compiles without syntax errors: `uv run python -m zettelkasten_mcp --help`
- [ ] No SSE references in active code paths

---

## Testing During Development

**Quick Syntax Check:**
```bash
# Verify no import errors
uv run python -c "from zettelkasten_mcp.server.mcp_server import ZettelkastenMcpServer; print('OK')"
```

**Check Config Load:**
```bash
# Verify config loads without errors
uv run python -c "from zettelkasten_mcp.config import config; print(f'stateless_http={config.stateless_http}')"
```

---

## Time Estimate

**Total: 1-2 hours**

- Update MCP server init: 5 minutes
- Update config class: 10 minutes
- Update main entry point: 20 minutes
- Update health check: 5 minutes
- Search and verify: 15 minutes
- Testing and verification: 20 minutes
- Buffer for issues: 25 minutes

---

## Known Risks

**🟢 Low Risk: API Compatibility**
- `http_app()` method exists in MCP SDK 1.22.0
- Parameters match documented API
- **Mitigation:** Verified in SDK changelog during Phase 1

**🟡 Medium Risk: Config Interactions**
- New config fields might conflict with environment variables
- **Mitigation:** Test config loading before running server

**🟢 Low Risk: Breaking Existing Functionality**
- Only HTTP transport affected (STDIO unchanged)
- **Mitigation:** Phase 4 will verify STDIO still works

---

## Notes

- Keep the old `sse_app()` code commented out temporarily (easier rollback)
- Document any unexpected behaviors in `.ai/artifacts/code-update-notes.md`
- Don't commit yet - wait for Phase 4 testing

---

**Previous Phase:** [Phase 2: Upgrade Dependencies](./streamable-http-implementation.phase-2.md)
**Next Phase:** [Phase 4: Testing & Validation](./streamable-http-implementation.phase-4.md)
