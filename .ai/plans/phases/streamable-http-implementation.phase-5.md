---
id: 30D2EEC2-400A-4EDC-A704-472908C6CAC5
title: "Phase 5: Docker & Deployment Updates"
status: ✅ Completed
date: 2025-11-22
author: aRustyDev
related:
  - 2F7850D8-3E51-456C-AE60-C70BAF323BFB  # Plan: Streamable HTTP Implementation
  - 8D5A8B21-C4A9-449D-A4B4-A1B29087B91B  # Phase 4: Testing & Validation
---

# Phase 5: Docker & Deployment Updates

**Duration:** 15 minutes (configuration only)
**Status:** ✅ Completed (2025-11-22)

---

## Objective

Update Docker configuration for Streamable HTTP deployment with Traefik routing.

---

## Tasks

### 5.1 Verify Dockerfile

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/docker/Dockerfile`

**Check CMD line:**
```dockerfile
# Line 71 (approximately) - should already be correct
CMD ["--transport", "http"]
```

**Why No Changes Needed:**
- CMD was already fixed in previous session to avoid env var expansion
- `--transport http` correctly triggers HTTP transport
- Server reads host/port from environment variables (via Pydantic config)
- No hardcoded ports in CMD (good practice)

**Verify with:**
```bash
# Check CMD is correct
grep "^CMD" docker/Dockerfile
# Expected: CMD ["--transport", "http"]
```

**If CMD is incorrect, update it:**
```dockerfile
# Remove any port/host arguments
CMD ["--transport", "http"]
```

---

### 5.2 Update docker-compose.yaml Traefik Labels

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/docker/docker-compose.yaml`

**Current Labels (Legacy HTTP+SSE):**
```yaml
labels:
  traefik.enable: true
  traefik.http.services.zettelkasten.loadbalancer.server.port: 8000

  # Old SSE endpoints
  traefik.http.routers.zettelkasten-sse.rule: Host(`mcp.localhost`) && PathPrefix(`/sse`)
  traefik.http.routers.zettelkasten-sse.service: zettelkasten
  traefik.http.routers.zettelkasten-sse.entrypoints: web,websecure

  traefik.http.routers.zettelkasten-messages.rule: Host(`mcp.localhost`) && PathPrefix(`/messages`)
  traefik.http.routers.zettelkasten-messages.service: zettelkasten
  traefik.http.routers.zettelkasten-messages.entrypoints: web,websecure

  # Health check
  traefik.http.routers.zettelkasten-health.rule: Host(`mcp.localhost`) && Path(`/health`)
  traefik.http.routers.zettelkasten-health.service: zettelkasten
  traefik.http.routers.zettelkasten-health.entrypoints: web,websecure
```

**New Labels (Streamable HTTP):**
```yaml
labels:
  traefik.enable: true
  traefik.http.services.zettelkasten.loadbalancer.server.port: 8000

  # Streamable HTTP endpoint (NEW)
  traefik.http.routers.zettelkasten-mcp.rule: Host(`mcp.localhost`) && PathPrefix(`/mcp`)
  traefik.http.routers.zettelkasten-mcp.service: zettelkasten
  traefik.http.routers.zettelkasten-mcp.entrypoints: web,websecure

  # Health check (unchanged)
  traefik.http.routers.zettelkasten-health.rule: Host(`mcp.localhost`) && Path(`/health`)
  traefik.http.routers.zettelkasten-health.service: zettelkasten
  traefik.http.routers.zettelkasten-health.entrypoints: web,websecure
```

**Changes:**
- ❌ **Removed:** `zettelkasten-sse` router (old `/sse` endpoint)
- ❌ **Removed:** `zettelkasten-messages` router (old `/messages/` endpoint)
- ✅ **Added:** `zettelkasten-mcp` router (new `/mcp` endpoint)
- ✅ **Kept:** Health check router (unchanged)

---

### 5.3 Rebuild Docker Image

```bash
cd /Users/arustydev/repos/mcp/zettelkasten-mcp/docker

# Build new image with updated dependencies
docker-compose build

# Expected output:
# Building zettelkasten
# ...
# Successfully built <image-id>
# Successfully tagged zettelkasten-mcp:local
```

**What Happens:**
1. Dockerfile runs `uv sync` with updated `pyproject.toml`
2. MCP SDK 1.22.0 gets installed in the image
3. New dependencies are baked into the image
4. Image is tagged as `zettelkasten-mcp:local`

**Expected Duration:** 2-5 minutes (depending on caching)

**If Build Fails:**
- Check error message for dependency conflicts
- Verify `pyproject.toml` is correct
- Try `docker-compose build --no-cache` for clean build

---

### 5.4 Test Docker Container

**Start Container:**
```bash
# Start container in detached mode
docker-compose up -d

# Check container status
docker-compose ps
# Expected: zettelkasten-mcp-http | running
```

**Check Logs:**
```bash
# View container logs
docker-compose logs -f zettelkasten

# Expected output:
# INFO: Using SQLite database: sqlite:///data/db/zettelkasten.db
# INFO: Starting Zettelkasten MCP server
# INFO: Zettelkasten MCP server initialized
# INFO: Starting HTTP server on 0.0.0.0:8000
# INFO: Uvicorn running on http://0.0.0.0:8000
```

**Red Flags:**
- ❌ Container exits immediately (check logs for errors)
- ❌ Import errors related to MCP SDK
- ❌ "http_app not found" errors
- ❌ Port binding failures

**Test Health Endpoint:**
```bash
# Test health check through Docker
curl -s http://localhost:8000/health | jq

# Expected:
# {
#   "status": "healthy",
#   "service": "zettelkasten-mcp",
#   "transport": "streamable-http"
# }
```

**Test Streamable HTTP Endpoint:**
```bash
# Test POST /mcp through Docker
curl -v -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' \
  2>&1 | grep "HTTP/1.1"

# Expected: HTTP/1.1 202 Accepted (NOT 405!)
```

---

### 5.5 Test via Traefik Proxy (If Configured)

**Prerequisites:**
- Traefik container must be running
- Host entry for `mcp.localhost` (usually works by default)

**Test Through Traefik:**
```bash
# Test health endpoint through Traefik
curl -s http://mcp.localhost/health | jq

# Expected: Same as direct test (200 OK, correct JSON)

# Test MCP endpoint through Traefik
curl -I http://mcp.localhost/mcp

# Expected: 200 OK or 405 (depending on how Traefik handles GET)
```

**Verify Traefik Routing:**
```bash
# Check Traefik dashboard (if enabled)
# Visit: http://localhost:8080 (default Traefik port)
# Verify:
#   - zettelkasten-mcp router exists
#   - Route: mcp.localhost/mcp → zettelkasten:8000
#   - Status: healthy (green)
```

**If Routing Fails:**
- Check Traefik container logs: `docker logs traefik`
- Verify labels are correct in docker-compose.yaml
- Ensure Traefik network is configured correctly
- Test direct connection first (bypass Traefik)

---

### 5.6 Stop and Clean Up

```bash
# Stop container
docker-compose down

# Expected output:
# Stopping zettelkasten-mcp-http ... done
# Removing zettelkasten-mcp-http ... done
# Removing network docker_default ... done

# Optional: Clean up old images
docker image prune -f

# Expected: Removes dangling images from previous builds
```

**When to Clean:**
- After successful testing
- Before committing changes
- To free up disk space

---

## Deliverables

After completing this phase, you should have:

- ✅ Dockerfile verified (CMD correct, no changes needed)
- ✅ docker-compose.yaml updated with new Traefik labels:
  - `/mcp` endpoint routed
  - `/sse` and `/messages/` endpoints removed
  - Health check unchanged
- ✅ Docker image built successfully with MCP SDK 1.22.0
- ✅ Container starts and runs without errors
- ✅ Health endpoint accessible through Docker
- ✅ `/mcp` endpoint accepts POST requests
- ✅ Traefik routing works correctly (if applicable)
- ✅ Container stops cleanly

---

## Verification Checklist

Before proceeding to Phase 6:

- [ ] `docker/Dockerfile` CMD is `["--transport", "http"]`
- [ ] `docker/docker-compose.yaml` has `/mcp` router (not `/sse`)
- [ ] `docker-compose build` succeeds without errors
- [ ] `docker-compose up -d` starts container successfully
- [ ] `docker-compose logs` shows "Uvicorn running on http://0.0.0.0:8000"
- [ ] `curl http://localhost:8000/health` returns correct response
- [ ] `curl -X POST http://localhost:8000/mcp` returns 202 Accepted
- [ ] Traefik routes to `/mcp` correctly (if using Traefik)
- [ ] `docker-compose down` stops container cleanly

---

## Configuration Reference

**docker-compose.yaml Full Labels Section:**
```yaml
services:
  zettelkasten:
    # ... other config ...
    labels:
      # Enable Traefik
      traefik.enable: true

      # Define backend service
      traefik.http.services.zettelkasten.loadbalancer.server.port: 8000

      # Route for Streamable HTTP (/mcp)
      traefik.http.routers.zettelkasten-mcp.rule: Host(`mcp.localhost`) && PathPrefix(`/mcp`)
      traefik.http.routers.zettelkasten-mcp.service: zettelkasten
      traefik.http.routers.zettelkasten-mcp.entrypoints: web,websecure

      # Route for health check
      traefik.http.routers.zettelkasten-health.rule: Host(`mcp.localhost`) && Path(`/health`)
      traefik.http.routers.zettelkasten-health.service: zettelkasten
      traefik.http.routers.zettelkasten-health.entrypoints: web,websecure
```

---

## Time Estimate

**Total: 1 hour**

- Verify Dockerfile: 5 minutes
- Update docker-compose.yaml: 10 minutes
- Rebuild image: 5 minutes
- Test container: 15 minutes
- Test through Traefik: 10 minutes
- Cleanup and documentation: 10 minutes
- Buffer: 5 minutes

---

## Known Risks

**🟢 Low Risk: Dockerfile Already Correct**
- CMD was fixed in previous session
- No changes needed
- **Mitigation:** Quick verification sufficient

**🟡 Medium Risk: Traefik Label Errors**
- Typos in labels can break routing
- **Mitigation:** Test direct connection first, then Traefik

**🟢 Low Risk: Build Failures**
- Dependencies should resolve cleanly (tested in Phase 2)
- **Mitigation:** Use --no-cache if issues occur

---

## Notes

- Keep old docker-compose.yaml labels commented for reference
- Test direct connection before testing through Traefik
- Document any Traefik-specific configuration issues

---

**Previous Phase:** [Phase 4: Testing & Validation](./streamable-http-implementation.phase-4.md)
**Next Phase:** [Phase 6: Documentation Updates](./streamable-http-implementation.phase-6.md)
