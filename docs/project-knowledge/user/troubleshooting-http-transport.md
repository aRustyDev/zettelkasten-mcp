# HTTP Transport Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Server Won't Start

**Symptom:**
```
Address already in use: 0.0.0.0:8000
```

**Cause:** Port 8000 is already in use by another application.

**Solutions:**
1. Use a different port:
   ```bash
   python -m zettelkasten_mcp.main --transport http --port 8001
   ```

2. Find and stop the conflicting process:
   ```bash
   # macOS/Linux
   lsof -i :8000
   kill <PID>

   # Or use a different port
   ```

3. Use environment variable:
   ```bash
   export ZETTELKASTEN_HTTP_PORT=8001
   python -m zettelkasten_mcp.main --transport http
   ```

---

### Issue 2: Cannot Connect from Remote Machine

**Symptom:**
```
Connection refused when connecting from another machine
```

**Cause:** Server is bound to `127.0.0.1` (localhost only).

**Solution:**
Bind to all interfaces:
```bash
python -m zettelkasten_mcp.main --transport http --host 0.0.0.0
```

Or via environment variable:
```bash
export ZETTELKASTEN_HTTP_HOST=0.0.0.0
python -m zettelkasten_mcp.main --transport http
```

**Security Note:** Only bind to `0.0.0.0` if you need remote access and have proper security measures (firewall, reverse proxy, etc.).

---

### Issue 3: CORS Errors in Browser

**Symptom:**
```
Access to fetch at 'http://localhost:8000/mcp' from origin 'https://app.example.com'
has been blocked by CORS policy
```

**Cause:** CORS is not enabled or origins not configured.

**Solution:**
Enable CORS and configure origins:
```bash
export ZETTELKASTEN_HTTP_CORS=true
export ZETTELKASTEN_HTTP_CORS_ORIGINS=https://app.example.com
python -m zettelkasten_mcp.main --transport http
```

Or with CLI:
```bash
python -m zettelkasten_mcp.main --transport http --cors
```

For multiple origins:
```bash
export ZETTELKASTEN_HTTP_CORS_ORIGINS=https://app.example.com,https://dev.example.com
```

---

### Issue 4: Missing Mcp-Session-Id Header

**Symptom:**
```
MCP client error: Missing Mcp-Session-Id header
```

**Cause:** CORS middleware not exposing required header.

**Solution:**
This should be automatic when using `--cors` flag. If you see this error:

1. Verify CORS is enabled:
   ```bash
   python -m zettelkasten_mcp.main --transport http --cors
   ```

2. Check server logs for CORS middleware initialization:
   ```
   INFO: Starting HTTP server on 0.0.0.0:8000 with CORS enabled
   ```

3. If problem persists, file a bug report with:
   - Server version
   - Command used to start server
   - Client being used
   - Full error message

---

### Issue 5: Slow Response Times

**Symptom:**
Server responds slowly to requests.

**Possible Causes and Solutions:**

1. **Database Lock Contention**
   - Symptom: Slow after many operations
   - Solution: Restart server, consider optimizing queries

2. **Large Number of Notes**
   - Symptom: Search operations slow
   - Solution: Normal for large datasets, consider pagination

3. **Network Latency**
   - Symptom: Slow from remote clients only
   - Solution: Use server closer to clients, check network

4. **Resource Constraints**
   - Symptom: Slow overall
   - Solution: Check server CPU/memory, increase resources

---

### Issue 6: Module Not Found Error

**Symptom:**
```
No module named 'zettelkasten_mcp'
```

**Cause:** Package not installed or virtual environment not activated.

**Solution:**
1. Activate virtual environment:
   ```bash
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

2. Install package:
   ```bash
   uv sync
   # or
   pip install -e .
   ```

3. Verify installation:
   ```bash
   python -c "import zettelkasten_mcp; print(zettelkasten_mcp.__file__)"
   ```

---

### Issue 7: uvicorn or starlette Not Found

**Symptom:**
```
ModuleNotFoundError: No module named 'uvicorn'
```

**Cause:** HTTP dependencies not installed.

**Solution:**
Install dependencies:
```bash
uv sync
# or
pip install starlette uvicorn
```

Verify:
```bash
python -c "import uvicorn; import starlette; print('OK')"
```

---

### Issue 8: Environment Variables Not Working

**Symptom:**
Environment variables don't affect configuration.

**Cause:** CLI arguments override environment variables.

**Solution:**
Check configuration precedence (CLI > ENV > Config):

1. Remove CLI arguments to use environment variables:
   ```bash
   # This ignores ZETTELKASTEN_HTTP_PORT
   export ZETTELKASTEN_HTTP_PORT=9000
   python -m zettelkasten_mcp.main --transport http --port 8000
   # Uses port 8000 (CLI wins)

   # This uses ZETTELKASTEN_HTTP_PORT
   export ZETTELKASTEN_HTTP_PORT=9000
   python -m zettelkasten_mcp.main --transport http
   # Uses port 9000 (ENV variable)
   ```

2. Verify environment variables are set:
   ```bash
   echo $ZETTELKASTEN_HTTP_PORT
   env | grep ZETTELKASTEN
   ```

---

### Issue 9: Docker Container Won't Start

**Symptom:**
Docker container exits immediately or fails healthcheck.

**Solution:**
1. Check logs:
   ```bash
   docker-compose -f docker/docker-compose.http.yml logs
   ```

2. Verify environment variables in `docker/.env`:
   ```bash
   cat docker/.env
   ```

3. Check port conflicts:
   ```bash
   docker ps | grep 8000
   lsof -i :8000
   ```

4. Manually run container to see errors:
   ```bash
   docker run -it --rm \
     -p 8000:8000 \
     zettelkasten-mcp:http \
     --transport http
   ```

---

### Issue 10: Cannot Access from Claude Code CLI

**Symptom:**
```
Failed to connect to MCP server
```

**Solutions:**
1. Verify server is running:
   ```bash
   curl http://localhost:8000/health
   # Should return 200 OK
   ```

2. Check MCP endpoint specifically:
   ```bash
   curl -v http://localhost:8000/mcp
   # Should show SSE connection headers
   ```

3. Verify URL format when adding:
   ```bash
   # Correct format (note /mcp endpoint)
   claude mcp add --transport http zettelkasten http://localhost:8000/mcp

   # Wrong (missing /mcp)
   claude mcp add --transport http zettelkasten http://localhost:8000
   ```

4. Check firewall/security software blocking connections

---

## Diagnostic Commands

### Check if Server is Running
```bash
# macOS/Linux
lsof -i :8000 -P -n | grep LISTEN

# Or using curl
curl -I http://localhost:8000/health
```

### View Server Logs
```bash
# If running in foreground, logs appear in terminal

# Docker:
docker-compose -f docker/docker-compose.http.yml logs -f

# Systemd:
journalctl -u zettelkasten-mcp -f
```

### Test CORS Configuration
```bash
curl -v -X OPTIONS http://localhost:8000/mcp \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST"

# Look for:
# Access-Control-Allow-Origin: https://example.com
# Access-Control-Expose-Headers: Mcp-Session-Id
```

### Verify Environment Variables
```bash
# Show all ZETTELKASTEN variables
env | grep ZETTELKASTEN

# Test with specific config
ZETTELKASTEN_HTTP_PORT=9999 python -m zettelkasten_mcp.main --transport http &
sleep 2
lsof -i :9999 | grep LISTEN
kill %1
```

---

## Getting Help

If you still have issues:

1. **Check README**: [README.md](../../README.md)
2. **Search Issues**: https://github.com/entanglr/zettelkasten-mcp/issues
3. **File Bug Report**: Include:
   - Command used to start server
   - Full error message
   - Server version
   - OS and Python version
   - Relevant logs
