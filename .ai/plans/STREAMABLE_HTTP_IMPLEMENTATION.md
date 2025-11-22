---
id: 2F7850D8-3E51-456C-AE60-C70BAF323BFB
title: Streamable HTTP via MCP SDK 1.22.0 Upgrade - Implementation Plan
status: 🔄 In Progress - Phase 3
date: 2025-11-22
author: aRustyDev
related:
  - FF1F3BCB-1328-41E3-9B7C-60946539384A  # Doc: MCP HTTP Transport Protocols
  - 82D15E44-AA64-4624-AE3E-3C2E5BAC97B3  # Doc: Streamable HTTP Implementation Options
  - 6E8A9F2C-1D4B-4E5A-9C3E-7F4B2D1A8E6C  # Doc: FastMCP Deep Dive Comparison
  - 9282B346-B74A-4522-B79C-690705DC1C92  # ADR: HTTP Transport Architecture
phases:
  - 3EC53936-B5CC-425D-804B-ED865033880B  # Phase 1: Preparation & Analysis
  - 4F557F9D-D5A9-4ACD-88D2-C741353CAC20  # Phase 2: Upgrade Dependencies
  - F628B564-5D2F-4A64-A658-4FDA04E2256D  # Phase 3: Code Updates for Streamable HTTP
  - 8D5A8B21-C4A9-449D-A4B4-A1B29087B91B  # Phase 4: Testing & Validation
  - 30D2EEC2-400A-4EDC-A704-472908C6CAC5  # Phase 5: Docker & Deployment Updates
  - E27EB7DB-14B0-4505-8B5B-2FCA30DF2A23  # Phase 6: Documentation Updates
---

# Streamable HTTP Implementation Plan - Option A

**Strategy:** Upgrade MCP SDK from 1.6.0 → 1.22.0
**Estimated Time:** 4-6 hours
**Risk Level:** 🟡 Medium (16 minor version jump)
**Complexity:** ⭐ Low (minimal code changes)

---

## Executive Summary

This plan implements **Modern Streamable HTTP transport** by upgrading the official MCP Python SDK from version 1.6.0 to 1.22.0. This is the recommended approach because:

✅ **Minimal Changes**: Only dependency upgrade + small config changes
✅ **Official Support**: Anthropic-backed, long-term stable
✅ **PR-Friendly**: Best for upstream contribution
✅ **Low Risk**: FastMCP 1.0 API is stable across versions
✅ **Fast Implementation**: 4-6 hours total

**Alternative Considered:** FastMCP 2.0 (standalone) - rejected due to higher migration effort and upstream PR concerns. See [fastmcp-deep-dive-comparison.md](../../docs/project-knowledge/dev/fastmcp-deep-dive-comparison.md) for analysis.

---

## Problem Statement

### Current Situation

**Server Configuration:**
- MCP SDK Version: `1.6.0`
- Transport: Legacy HTTP+SSE (2024-11-05 spec)
- Endpoints: `/sse` (GET), `/messages/` (POST)

**Client Compatibility Issues:**
- ❌ **Zed Editor**: Times out after 60 seconds
- ❌ **Modern MCP Clients**: Expect POST `/mcp` → 405 error
- ⚠️ **Deprecated Protocol**: Limits future compatibility

### Root Cause

**Protocol Version Mismatch:**
```
Server:  Legacy HTTP+SSE  → /sse (GET), /messages/ (POST)
Zed:     Streamable HTTP  → /mcp (POST/GET/DELETE)
Result:  405 error on POST /sse → timeout
```

**Why 405 is Correct:**
The Legacy protocol's `/sse` endpoint only accepts GET requests. When Zed sends POST `/sse`, the server correctly returns 405 Method Not Allowed. This is **not a bug**, it's a **protocol incompatibility**.

**Technical Details:** See [mcp-http-transport-protocols.md](../../docs/project-knowledge/dev/mcp-http-transport-protocols.md)

---

## Solution: Upgrade to MCP SDK 1.22.0

### Why This Works

**MCP SDK 1.8.0** (released May 8, 2025) added Streamable HTTP support:
- ✅ Implements Modern Streamable HTTP (2025-03-26 spec)
- ✅ Single `/mcp` endpoint (GET/POST/DELETE)
- ✅ Session management via `Mcp-Session-Id` header
- ✅ Backward compatible with STDIO transport

**Current Latest:** 1.22.0 (released November 20, 2025)
- ✅ Mature implementation (14 versions since Streamable HTTP)
- ✅ Bug fixes and performance improvements
- ✅ Full protocol compliance

### Changes Required

**Minimal Code Impact:**
1. Update `pyproject.toml`: `mcp[cli]>=1.22.0`
2. Add `stateless_http=True` to FastMCP initialization
3. Change transport string: `"sse"` → `"streamable-http"`
4. Run tests, rebuild Docker image

**No Breaking Changes Expected:**
- FastMCP 1.0 decorator API is stable
- Same import path: `from mcp.server.fastmcp import FastMCP`
- Existing tools/resources/prompts unchanged
- SQLAlchemy service layer unchanged

---

## Implementation Phases

### Phase 1: Preparation & Analysis (1 hour)

**Objective:** Understand changes between 1.6.0 and 1.22.0, prepare environment

#### Tasks:

**1.1 Create Feature Branch**
```bash
cd /Users/arustydev/repos/mcp/zettelkasten-mcp
git checkout -b feat/upgrade-mcp-sdk-1.22
git push -u origin feat/upgrade-mcp-sdk-1.22
```

**1.2 Review MCP SDK Changelog**
- Visit: https://github.com/modelcontextprotocol/python-sdk/releases
- Review breaking changes from v1.6.0 → v1.22.0
- Document any API changes affecting our codebase

**1.3 Backup Current State**
```bash
# Document current behavior
uv pip list > .ai/artifacts/pre-upgrade-packages.txt
python -c "from mcp.server.fastmcp import FastMCP; print(FastMCP.__doc__)" > .ai/artifacts/pre-upgrade-fastmcp-api.txt

# Create test baseline
uv run pytest --verbose > .ai/artifacts/pre-upgrade-test-results.txt 2>&1 || true
```

**1.4 Document Current Endpoints**
```bash
# Start server and document endpoints
ZETTELKASTEN_HTTP_PORT=9000 uv run python -m zettelkasten_mcp --transport http &
SERVER_PID=$!
sleep 3

# Test current endpoints
curl -v http://localhost:9000/health 2>&1 | tee .ai/artifacts/pre-upgrade-health.txt
curl -v http://localhost:9000/sse 2>&1 | tee .ai/artifacts/pre-upgrade-sse.txt
curl -X HEAD http://localhost:9000/mcp 2>&1 | tee .ai/artifacts/pre-upgrade-mcp-404.txt

kill $SERVER_PID
```

**Deliverables:**
- ✅ Feature branch created
- ✅ Changelog reviewed and documented
- ✅ Current state backed up
- ✅ Baseline test results captured

**Time Estimate:** 1 hour

---

### Phase 2: Upgrade Dependencies (1 hour)

**Objective:** Upgrade MCP SDK to 1.22.0 and resolve dependency conflicts

#### Tasks:

**2.1 Update pyproject.toml**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/pyproject.toml`

```diff
 [project]
 dependencies = [
-    "mcp[cli]>=1.2.0",
+    "mcp[cli]>=1.22.0",
     "sqlalchemy>=2.0.0",
     "pydantic>=2.0.0",
     "python-frontmatter>=1.0.0",
     "markdown>=3.4.0",
     "python-dotenv>=1.0.0",
     "starlette>=0.27.0",
     "uvicorn>=0.23.0",
 ]
```

**2.2 Upgrade Dependencies**
```bash
cd /Users/arustydev/repos/mcp/zettelkasten-mcp

# Remove old lock file to force fresh resolution
rm uv.lock

# Sync dependencies
uv sync

# Verify upgrade
uv pip show mcp
# Expected output: Version: 1.22.0 (or latest)
```

**2.3 Check for Dependency Conflicts**
```bash
# List all installed packages
uv pip list > .ai/artifacts/post-upgrade-packages.txt

# Check for version conflicts
uv pip check

# Compare with pre-upgrade
diff .ai/artifacts/pre-upgrade-packages.txt .ai/artifacts/post-upgrade-packages.txt > .ai/artifacts/package-diff.txt
```

**2.4 Verify Import Still Works**
```bash
# Quick smoke test
uv run python -c "from mcp.server.fastmcp import FastMCP, Context; print('Import successful')"
```

**Deliverables:**
- ✅ `pyproject.toml` updated
- ✅ Dependencies upgraded
- ✅ No dependency conflicts
- ✅ Imports still work

**Time Estimate:** 1 hour

**Rollback Plan:**
```bash
# If upgrade fails
git checkout pyproject.toml uv.lock
uv sync
```

---

### Phase 3: Code Updates for Streamable HTTP (1-2 hours)

**Objective:** Update code to use Streamable HTTP transport

#### Tasks:

**3.1 Update MCP Server Initialization**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/src/zettelkasten_mcp/server/mcp_server.py`

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
- Recommended for Streamable HTTP deployments
- Each request gets a new transport instance
- Better for load balancing and horizontal scaling
- Matches Zed's expected behavior

**3.2 Update Transport Configuration**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/src/zettelkasten_mcp/config.py`

Check if there are any hardcoded transport strings:

```python
# Review config.py for any SSE-specific settings
# May need to add streamable_http_path if customized
```

**3.3 Update Main Entry Point**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/src/zettelkasten_mcp/__main__.py`

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

**3.4 Update Config Class (if needed)**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/src/zettelkasten_mcp/config.py`

Add `stateless_http` configuration:

```python
class Config(BaseSettings):
    # ... existing fields ...

    # HTTP Transport Settings
    http_host: str = "0.0.0.0"
    http_port: int = 8000
    stateless_http: bool = True  # NEW: Enable stateless HTTP mode
    streamable_http_path: str = "/mcp"  # NEW: Streamable HTTP endpoint path
```

**3.5 Verify Health Check Endpoint**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/src/zettelkasten_mcp/server/mcp_server.py`

Ensure health check stays unchanged:

```python
async def health_check(request):
    """Health check endpoint for Docker/Kubernetes monitoring."""
    from starlette.responses import JSONResponse

    return JSONResponse({
        "status": "healthy",
        "service": "zettelkasten-mcp",
        "transport": "streamable-http"  # UPDATE transport name
    })
```

**Deliverables:**
- ✅ MCP server initialization updated with `stateless_http=True`
- ✅ Transport method changed from SSE to Streamable HTTP
- ✅ Main entry point updated to use `http_app()`
- ✅ Config class updated (if needed)
- ✅ Health check reflects new transport

**Time Estimate:** 1-2 hours

---

### Phase 4: Testing & Validation (2-3 hours)

**Objective:** Verify all functionality works with Streamable HTTP

#### Tasks:

**4.1 Unit Tests**
```bash
cd /Users/arustydev/repos/mcp/zettelkasten-mcp

# Run existing test suite
uv run pytest --verbose

# Expected: All tests pass (no breaking changes in FastMCP 1.0 API)
```

**4.2 Manual STDIO Transport Test**
```bash
# Verify backward compatibility with STDIO
uv run python -m zettelkasten_mcp --transport stdio

# In another terminal, test with MCP client
npx @modelcontextprotocol/inspector python -m zettelkasten_mcp --transport stdio
```

Expected: STDIO transport still works (no regression)

**4.3 Start HTTP Server (Streamable HTTP)**
```bash
# Start server with new transport
ZETTELKASTEN_HTTP_PORT=8000 uv run python -m zettelkasten_mcp --transport http

# Should see:
# INFO: Starting HTTP server on 0.0.0.0:8000
# INFO: Uvicorn running on http://0.0.0.0:8000
```

**4.4 Test Health Endpoint**
```bash
# Health check should still work
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","service":"zettelkasten-mcp","transport":"streamable-http"}
```

**4.5 Test Streamable HTTP Endpoint**
```bash
# Test GET /mcp (should return 200 or upgrade to SSE)
curl -v http://localhost:8000/mcp

# Test POST /mcp (should return 202 Accepted or start SSE)
curl -v -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'

# Expected: 202 Accepted (not 405!)
```

**4.6 Test with Zed Editor**

Update Zed MCP config:

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

**Expected Behavior:**
- ✅ Zed connects successfully (no 60-second timeout)
- ✅ Tools are listed in Zed's MCP tool palette
- ✅ Calling a tool returns results

**4.7 Test with mcp-remote (Backward Compatibility)**
```bash
# Test with mcp-remote client
npx mcp-remote http://localhost:8000/mcp

# Expected: Connection successful, tools listed
```

**4.8 Verify Legacy Endpoints Return 404**
```bash
# Old endpoints should no longer exist
curl -I http://localhost:8000/sse
# Expected: 404 Not Found (or redirect to /mcp)

curl -I http://localhost:8000/messages/
# Expected: 404 Not Found
```

**4.9 Load Testing (Optional)**
```bash
# Simple load test with hey
hey -n 1000 -c 10 http://localhost:8000/health

# Expected: All requests succeed, reasonable latency
```

**Deliverables:**
- ✅ All unit tests pass
- ✅ STDIO transport still works
- ✅ HTTP server starts successfully
- ✅ Health endpoint responds
- ✅ `/mcp` endpoint accepts POST (no 405!)
- ✅ Zed connects successfully
- ✅ mcp-remote works
- ✅ Legacy endpoints return 404

**Time Estimate:** 2-3 hours

---

### Phase 5: Docker & Deployment Updates (1 hour)

**Objective:** Update Docker configuration for Streamable HTTP

#### Tasks:

**5.1 Update Dockerfile (if needed)**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/docker/Dockerfile`

Verify CMD is correct:

```dockerfile
# Should already be correct (no port/host in CMD)
CMD ["--transport", "http"]
```

No changes needed (already fixed in previous session).

**5.2 Update docker-compose.yaml Labels**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/docker/docker-compose.yaml`

Update Traefik labels for new endpoint:

```diff
 labels:
   traefik.enable: true
   traefik.http.services.zettelkasten.loadbalancer.server.port: 8000

-  # Old SSE endpoints
-  traefik.http.routers.zettelkasten-sse.rule: Host(`mcp.localhost`) && PathPrefix(`/sse`)
-  traefik.http.routers.zettelkasten-messages.rule: Host(`mcp.localhost`) && PathPrefix(`/messages`)

+  # Streamable HTTP endpoint
+  traefik.http.routers.zettelkasten-mcp.rule: Host(`mcp.localhost`) && PathPrefix(`/mcp`)
+  traefik.http.routers.zettelkasten-mcp.service: zettelkasten
+  traefik.http.routers.zettelkasten-mcp.entrypoints: web,websecure

   # Health check (unchanged)
   traefik.http.routers.zettelkasten-health.rule: Host(`mcp.localhost`) && Path(`/health`)
   traefik.http.routers.zettelkasten-health.service: zettelkasten
```

**5.3 Rebuild Docker Image**
```bash
cd /Users/arustydev/repos/mcp/zettelkasten-mcp/docker

# Build new image
docker-compose build

# Expected: Build succeeds with updated dependencies
```

**5.4 Test Docker Container**
```bash
# Start container
docker-compose up -d

# Check logs
docker-compose logs -f zettelkasten

# Expected:
# INFO: Starting HTTP server on 0.0.0.0:8000
# INFO: Uvicorn running on http://0.0.0.0:8000

# Verify health
curl http://localhost:8000/health

# Test Streamable HTTP endpoint
curl -v http://localhost:8000/mcp
```

**5.5 Test via Traefik (if configured)**
```bash
# Test through Traefik proxy
curl http://mcp.localhost/health
curl http://mcp.localhost/mcp

# Expected: Routes correctly to container
```

**5.6 Stop and Clean Up**
```bash
# Stop container
docker-compose down

# Optional: Clean up old images
docker image prune -f
```

**Deliverables:**
- ✅ Dockerfile verified (no changes needed)
- ✅ docker-compose.yaml labels updated for `/mcp` endpoint
- ✅ Docker image builds successfully
- ✅ Container starts and serves traffic
- ✅ Health and MCP endpoints work through Docker
- ✅ Traefik routing works (if applicable)

**Time Estimate:** 1 hour

---

### Phase 6: Documentation Updates (1 hour)

**Objective:** Update documentation to reflect Streamable HTTP implementation

#### Tasks:

**6.1 Update README.md**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/README.md`

Update HTTP transport section:

```markdown
### HTTP Transport (Streamable HTTP)

The server supports Modern Streamable HTTP transport for remote access:

\`\`\`bash
uv run python -m zettelkasten_mcp --transport http --port 8000
\`\`\`

**Endpoint:** `http://localhost:8000/mcp`

**Connecting from Zed:**

\`\`\`json
{
  "context_servers": {
    "zettelkasten": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
\`\`\`

**Connecting with mcp-remote:**

\`\`\`bash
npx mcp-remote http://localhost:8000/mcp
\`\`\`

**Health Check:** `http://localhost:8000/health`
```

**6.2 Create Migration Guide**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/docs/migration/v1.6-to-v1.22-sdk-upgrade.md`

```markdown
# Migration Guide: MCP SDK 1.6.0 → 1.22.0

This guide covers the upgrade to MCP SDK 1.22.0 for Streamable HTTP support.

## Changes

### Dependency Upgrade
- **Before:** `mcp[cli]>=1.2.0` (resolved to 1.6.0)
- **After:** `mcp[cli]>=1.22.0`

### Transport Change
- **Before:** Legacy HTTP+SSE (`/sse`, `/messages/`)
- **After:** Modern Streamable HTTP (`/mcp`)

### Code Changes
1. Added `stateless_http=True` to FastMCP initialization
2. Changed transport from `"sse"` to `"streamable-http"`
3. Updated endpoint paths in Traefik labels

### Client Configuration
**Zed Editor:**
\`\`\`json
{
  "context_servers": {
    "zettelkasten": {
      "type": "http",
      "url": "http://localhost:8000/mcp"  // Changed from /sse
    }
  }
}
\`\`\`

## Backward Compatibility

✅ **STDIO transport:** Unchanged, fully compatible
❌ **Legacy HTTP+SSE:** Deprecated, removed in favor of Streamable HTTP

## Testing

See [Testing Guide](../testing/http-transport-testing.md)
```

**6.3 Update HTTP_IMPLEMENTATION.md**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/.ai/plans/HTTP_IMPLEMENTATION.md`

Update status to completed:

```diff
 ---
 id: 15754957-34F7-418C-8E2A-319175C225C3
-status: ✅ Completed
+status: 🗄️ Archived - Superseded by Streamable HTTP
+superseded_by: 2F7850D8-3E51-456C-AE60-C70BAF323BFB
 ---

+**Note:** This plan implemented Legacy HTTP+SSE transport. It has been superseded by the Streamable HTTP implementation (MCP SDK 1.22.0 upgrade).
```

**6.4 Update Project Knowledge Docs**

Update the status in:
- `docs/project-knowledge/dev/mcp-http-transport-protocols.md`
- `docs/project-knowledge/dev/streamable-http-implementation-options.md`

Mark as "✅ Implemented" with implementation date.

**6.5 Update CHANGELOG**

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/CHANGELOG.md` (or create it)

```markdown
# Changelog

## [Unreleased]

### Added
- Modern Streamable HTTP transport support (MCP SDK 1.22.0)
- Single unified `/mcp` endpoint for all HTTP operations
- Stateless HTTP mode for better scalability
- Zed editor compatibility

### Changed
- Upgraded MCP SDK from 1.6.0 to 1.22.0
- Migrated from Legacy HTTP+SSE to Modern Streamable HTTP
- Updated Docker Traefik labels for new endpoint

### Deprecated
- Legacy HTTP+SSE transport (`/sse`, `/messages/` endpoints)

### Removed
- None (STDIO transport remains fully supported)

### Fixed
- Zed editor 60-second timeout issue
- 405 Method Not Allowed errors with modern MCP clients
```

**Deliverables:**
- ✅ README.md updated with Streamable HTTP examples
- ✅ Migration guide created
- ✅ HTTP_IMPLEMENTATION.md marked as superseded
- ✅ Project knowledge docs updated
- ✅ CHANGELOG.md updated

**Time Estimate:** 1 hour

---

## Testing Strategy

### Automated Tests

**Unit Tests:**
```bash
# Run full test suite
uv run pytest --verbose --cov=zettelkasten_mcp

# Expected: All tests pass
```

**Integration Tests:**
- Test STDIO transport (backward compatibility)
- Test HTTP transport (Streamable HTTP)
- Test health endpoint
- Test all tools via MCP client

### Manual Tests

**Test Matrix:**

| Transport | Client | Expected Result |
|-----------|--------|----------------|
| STDIO | MCP Inspector | ✅ Works |
| STDIO | mcp-remote (stdio) | ✅ Works |
| HTTP | Zed Editor | ✅ Works (no timeout) |
| HTTP | mcp-remote (http) | ✅ Works |
| HTTP | curl (health) | ✅ Works |
| HTTP | curl (POST /mcp) | ✅ 202 Accepted |

**Success Criteria:**
- ✅ All automated tests pass
- ✅ STDIO transport unchanged (regression test)
- ✅ Zed connects without timeout
- ✅ All tools callable via HTTP
- ✅ Health endpoint returns 200 OK
- ✅ Docker deployment works

---

## Rollback Plan

### If Upgrade Fails

**Quick Rollback:**
```bash
# Revert git changes
git checkout pyproject.toml uv.lock
git checkout src/zettelkasten_mcp/

# Reinstall old dependencies
uv sync

# Verify rollback
uv pip show mcp  # Should show 1.6.0
uv run python -m zettelkasten_mcp --transport stdio
```

**Docker Rollback:**
```bash
# Revert docker-compose.yaml
git checkout docker/docker-compose.yaml

# Rebuild with old version
cd docker && docker-compose build && docker-compose up -d
```

### Known Risks

**🟡 Risk: Breaking Changes in 16 Minor Versions**
- **Mitigation:** Review changelog before upgrade
- **Mitigation:** Run full test suite after upgrade
- **Mitigation:** Keep rollback plan ready

**🟢 Risk: Dependency Conflicts**
- **Mitigation:** Fresh `uv.lock` resolution
- **Mitigation:** `uv pip check` to verify compatibility
- **Mitigation:** Test in development environment first

**🟢 Risk: FastMCP API Changes**
- **Mitigation:** FastMCP 1.0 API is stable across versions
- **Mitigation:** Decorator syntax unchanged since 1.0
- **Expected:** Very low risk

---

## Success Metrics

### Technical Metrics

- ✅ Zed connection time: < 2 seconds (was: 60s timeout)
- ✅ HTTP response time: < 100ms for health check
- ✅ Test coverage: Maintained or improved
- ✅ Zero regressions in STDIO transport

### Functional Metrics

- ✅ All 20+ MCP tools work via HTTP
- ✅ All resources accessible
- ✅ All prompts functional
- ✅ Docker deployment successful

### Documentation Metrics

- ✅ README.md updated
- ✅ Migration guide created
- ✅ Changelog updated
- ✅ API examples correct

---

## Timeline

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1: Preparation | 1 hour | T+0 | T+1 |
| Phase 2: Dependencies | 1 hour | T+1 | T+2 |
| Phase 3: Code Updates | 1-2 hours | T+2 | T+4 |
| Phase 4: Testing | 2-3 hours | T+4 | T+7 |
| Phase 5: Docker | 1 hour | T+7 | T+8 |
| Phase 6: Documentation | 1 hour | T+8 | T+9 |

**Total: 7-9 hours** (conservative estimate)
**Fast Track: 4-6 hours** (if no issues)

---

## Post-Implementation

### Verification Checklist

After implementation is complete:

- [ ] MCP SDK version is 1.22.0 (`uv pip show mcp`)
- [ ] All tests pass (`uv run pytest`)
- [ ] STDIO transport works (`uv run python -m zettelkasten_mcp --transport stdio`)
- [ ] HTTP server starts (`uv run python -m zettelkasten_mcp --transport http`)
- [ ] Health endpoint responds (`curl http://localhost:8000/health`)
- [ ] `/mcp` endpoint accepts POST (`curl -X POST http://localhost:8000/mcp`)
- [ ] Zed connects successfully (no timeout)
- [ ] mcp-remote works (`npx mcp-remote http://localhost:8000/mcp`)
- [ ] Docker build succeeds (`docker-compose build`)
- [ ] Docker container runs (`docker-compose up -d`)
- [ ] Documentation updated (README, migration guide, changelog)

### Cleanup Tasks

```bash
# Remove backup artifacts
rm -rf .ai/artifacts/pre-upgrade-*.txt
rm -rf .ai/artifacts/post-upgrade-*.txt

# Commit changes
git add .
git commit -m "feat: upgrade to MCP SDK 1.22.0 for Streamable HTTP support

- Upgrade mcp[cli] from 1.6.0 to 1.22.0
- Migrate from Legacy HTTP+SSE to Modern Streamable HTTP
- Update endpoint from /sse to /mcp
- Add stateless_http=True for better scalability
- Update Docker Traefik labels
- Update documentation and examples

Fixes Zed editor timeout issue
Enables compatibility with modern MCP clients

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin feat/upgrade-mcp-sdk-1.22
```

---

## Next Steps

After successful implementation:

1. **Create Pull Request**
   - Target: Upstream repository (if contributing)
   - Include: Migration guide, changelog, test results
   - Reference: This implementation plan

2. **Monitor Production**
   - Watch for errors in logs
   - Monitor connection success rate
   - Track performance metrics

3. **Update CI/CD**
   - Verify GitHub Actions run with new SDK
   - Update deployment scripts if needed

4. **Archive Old Documentation**
   - Mark Legacy HTTP+SSE docs as archived
   - Update references to point to Streamable HTTP docs

---

## References

- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP Specification (2025-03-26)**: https://modelcontextprotocol.io/specification/2025-03-26
- **FastMCP Documentation**: https://github.com/modelcontextprotocol/python-sdk/tree/main/src/mcp/server/fastmcp
- **Cloudflare Blog**: https://blog.cloudflare.com/streamable-http-mcp-servers-python/
- **Related Docs**:
  - [MCP HTTP Transport Protocols](../../docs/project-knowledge/dev/mcp-http-transport-protocols.md)
  - [Streamable HTTP Options Comparison](../../docs/project-knowledge/dev/streamable-http-implementation-options.md)
  - [FastMCP Deep Dive](../../docs/project-knowledge/dev/fastmcp-deep-dive-comparison.md)

---

**Plan Status:** 📋 Ready for Implementation
**Last Updated:** 2025-11-22
**Next Action:** Begin Phase 1 (Preparation)
