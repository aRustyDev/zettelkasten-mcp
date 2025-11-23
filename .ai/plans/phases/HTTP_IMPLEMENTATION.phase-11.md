---
id: 86EA6699-2DA0-4FBD-8BCE-1065A79B5431
title: HTTP Transport Implementation - Phase 11: User Documentation
status: ✅ Completed
date: 2025-11-21
author: aRustyDev
---
# HTTP Transport Implementation - Phase 11: User Documentation

**Status:** ✅ COMPLETED
**Date:** 2025-11-21
**Commit:** (pending)
**Plan:** [Back to main plan](../HTTP_IMPLEMENTATION.md)

---


### Overview
Create comprehensive user-facing documentation for HTTP transport usage, configuration, troubleshooting, and migration from STDIO.

### Step 11.1: Create HTTP Transport Usage Guide
**File:** `docs/project-knowledge/HTTP_USAGE.md`

**Content:**
```markdown
# HTTP Transport Usage Guide

## Quick Start

### Start the Server
```bash
# Basic HTTP server on port 8000
python -m zettelkasten_mcp.main --transport http

# Custom port
python -m zettelkasten_mcp.main --transport http --port 9000

# With CORS for browser clients
python -m zettelkasten_mcp.main --transport http --cors
```

### Connect with Claude Code CLI
```bash
# Add the MCP server
claude mcp add --transport http zettelkasten http://localhost:8000/mcp

# Verify connection
claude mcp list
```

## Configuration Options

### Command-Line Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--transport` | Transport type (stdio or http) | stdio |
| `--host` | HTTP host to bind to | 0.0.0.0 |
| `--port` | HTTP port to bind to | 8000 |
| `--cors` | Enable CORS middleware | false |

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `ZETTELKASTEN_HTTP_HOST` | HTTP host | 0.0.0.0 |
| `ZETTELKASTEN_HTTP_PORT` | HTTP port | 8000 |
| `ZETTELKASTEN_HTTP_CORS` | Enable CORS | false |
| `ZETTELKASTEN_HTTP_CORS_ORIGINS` | Allowed CORS origins | * |
| `ZETTELKASTEN_JSON_RESPONSE` | JSON response mode | true |

### Configuration Precedence
Configuration values are determined in this order (highest to lowest):
1. Command-line arguments
2. Environment variables
3. Config file defaults

Example:
```bash
# Environment variable sets port to 9000
export ZETTELKASTEN_HTTP_PORT=9000

# CLI argument overrides to 8080
python -m zettelkasten_mcp.main --transport http --port 8080
# Server runs on port 8080 (CLI wins)
```

## Usage Scenarios

### Scenario 1: Local Development
Run HTTP server locally for testing:
```bash
python -m zettelkasten_mcp.main --transport http --host 127.0.0.1 --port 8000
```

Connect from same machine:
```bash
claude mcp add --transport http zettelkasten http://127.0.0.1:8000/mcp
```

### Scenario 2: Remote Server
Run on remote server with environment variables:
```bash
export ZETTELKASTEN_HTTP_HOST=0.0.0.0
export ZETTELKASTEN_HTTP_PORT=8000
export ZETTELKASTEN_NOTES_DIR=/data/notes
export ZETTELKASTEN_DATABASE_PATH=/data/db/zettelkasten.db

python -m zettelkasten_mcp.main --transport http
```

Connect from client:
```bash
claude mcp add --transport http zettelkasten http://your-server.com:8000/mcp
```

### Scenario 3: Docker Deployment
Use docker-compose for production:
```bash
# Create .env file
cat > docker/.env <<EOF
ZETTELKASTEN_HTTP_PORT=8000
ZETTELKASTEN_NOTES_DIR=./data/notes
ZETTELKASTEN_DATABASE_DIR=./data/db
ZETTELKASTEN_HTTP_CORS=false
EOF

# Start with docker-compose
docker-compose -f docker/docker-compose.http.yml up -d

# Check logs
docker-compose -f docker/docker-compose.http.yml logs -f

# Connect from client
claude mcp add --transport http zettelkasten http://your-server.com:8000/mcp
```

### Scenario 4: Browser-Based Clients
Enable CORS for browser access:
```bash
export ZETTELKASTEN_HTTP_CORS=true
export ZETTELKASTEN_HTTP_CORS_ORIGINS=https://app.example.com,https://dev.example.com

python -m zettelkasten_mcp.main --transport http
```

Or with CLI:
```bash
python -m zettelkasten_mcp.main --transport http --cors
```

### Scenario 5: Multiple Instances
Run multiple servers on different ports:
```bash
# Instance 1: Personal notes
ZETTELKASTEN_HTTP_PORT=8001 \
ZETTELKASTEN_NOTES_DIR=~/personal-notes \
python -m zettelkasten_mcp.main --transport http &

# Instance 2: Work notes
ZETTELKASTEN_HTTP_PORT=8002 \
ZETTELKASTEN_NOTES_DIR=~/work-notes \
python -m zettelkasten_mcp.main --transport http &
```

## Security Considerations

### 1. No Built-in Authentication
⚠️ **WARNING**: The HTTP server has no built-in authentication. Anyone who can reach the server can access your notes.

**Recommendations:**
- Use a reverse proxy (nginx, Caddy) with authentication
- Run behind a VPN for remote access
- Use firewall rules to restrict access
- Don't expose directly to the internet

### 2. CORS Configuration
Only enable CORS if you need browser-based access:
```bash
# Specific origins (recommended)
export ZETTELKASTEN_HTTP_CORS_ORIGINS=https://app.example.com

# Wildcard (less secure)
export ZETTELKASTEN_HTTP_CORS_ORIGINS=*
```

### 3. HTTPS/TLS
The server doesn't provide TLS. Use a reverse proxy:

**Nginx Example:**
```nginx
server {
    listen 443 ssl;
    server_name notes.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 4. Network Binding
- `0.0.0.0`: Listen on all network interfaces (default)
- `127.0.0.1`: Listen only on localhost (local access only)

Choose based on your security needs:
```bash
# Local only
python -m zettelkasten_mcp.main --transport http --host 127.0.0.1

# All interfaces (for remote access)
python -m zettelkasten_mcp.main --transport http --host 0.0.0.0
```

## Troubleshooting

See [Troubleshooting Guide](user/troubleshooting-http-transport.md) for common issues and solutions.

## Migration from STDIO

See [Migration Guide](user/migration-stdio-to-http.md) for step-by-step instructions.
```

### Step 11.2: Create Troubleshooting Guide
**File:** `docs/project-knowledge/user/troubleshooting-http-transport.md`

**Content:**
```markdown
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
```

### Step 11.3: Create Migration Guide
**File:** `docs/project-knowledge/user/migration-stdio-to-http.md`

**Content:**
```markdown
# Migration Guide: STDIO to HTTP Transport

## Overview
This guide helps you migrate from STDIO transport (Claude Desktop) to HTTP transport for remote access or Docker deployment.

## Before You Start

### Understand the Differences

| Aspect | STDIO | HTTP |
|--------|-------|------|
| **Use Case** | Local Claude Desktop | Remote access, Docker |
| **Access** | Same machine only | Network accessible |
| **Authentication** | OS-level (process isolation) | None (use reverse proxy) |
| **Configuration** | Claude Desktop config file | CLI args or env vars |
| **Deployment** | Local only | Can containerize |

### When to Use Each Transport

**Continue using STDIO if:**
- Using Claude Desktop exclusively
- Working on local machine only
- No need for remote access
- Want simplest setup

**Switch to HTTP if:**
- Need remote access to server
- Want Docker deployment
- Using Claude Code CLI from different machines
- Building browser-based MCP clients
- Running multiple instances

## Migration Steps

### Step 1: Verify Current STDIO Setup

First, ensure your current STDIO setup works:

```bash
# Your current command (probably this)
python -m zettelkasten_mcp.main

# Or Claude Desktop starts it automatically via config
```

**Claude Desktop Config** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "zettelkasten": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "zettelkasten_mcp.main"],
      "env": {
        "ZETTELKASTEN_NOTES_DIR": "/path/to/notes",
        "ZETTELKASTEN_DATABASE_PATH": "/path/to/db/zettelkasten.db"
      }
    }
  }
}
```

### Step 2: Test HTTP Transport Locally

Before deploying remotely, test HTTP transport on your local machine:

```bash
# Start server with HTTP transport
python -m zettelkasten_mcp.main --transport http --host 127.0.0.1 --port 8000
```

You should see:
```
INFO: Starting HTTP server on 127.0.0.1:8000
INFO: Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Connect with Claude Code CLI

In a new terminal, connect using Claude Code CLI:

```bash
# Add the HTTP transport server
claude mcp add --transport http zettelkasten http://127.0.0.1:8000/mcp

# Verify it's listed
claude mcp list

# Test a command
claude "List my recent notes"
```

### Step 4: Configure Environment Variables

For production, use environment variables instead of CLI args:

```bash
# Create .env file
cat > ~/.zettelkasten.env <<EOF
# Notes and Database
ZETTELKASTEN_NOTES_DIR=/path/to/notes
ZETTELKASTEN_DATABASE_PATH=/path/to/db/zettelkasten.db

# HTTP Transport
ZETTELKASTEN_HTTP_HOST=0.0.0.0
ZETTELKASTEN_HTTP_PORT=8000
ZETTELKASTEN_HTTP_CORS=false

# Logging
ZETTELKASTEN_LOG_LEVEL=INFO
EOF

# Load and start server
set -a
source ~/.zettelkasten.env
set +a
python -m zettelkasten_mcp.main --transport http
```

### Step 5: Set Up as a System Service (Optional)

For persistent running, create a systemd service (Linux):

**Create** `/etc/systemd/system/zettelkasten-mcp.service`:
```ini
[Unit]
Description=Zettelkasten MCP HTTP Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/zettelkasten-mcp
EnvironmentFile=/home/youruser/.zettelkasten.env
ExecStart=/path/to/.venv/bin/python -m zettelkasten_mcp.main --transport http
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable zettelkasten-mcp
sudo systemctl start zettelkasten-mcp

# Check status
sudo systemctl status zettelkasten-mcp

# View logs
journalctl -u zettelkasten-mcp -f
```

### Step 6: Deploy with Docker (Optional)

For containerized deployment:

```bash
# Create data directories
mkdir -p data/notes data/db

# Create environment file
cat > docker/.env <<EOF
ZETTELKASTEN_HTTP_PORT=8000
ZETTELKASTEN_NOTES_DIR=./data/notes
ZETTELKASTEN_DATABASE_DIR=./data/db
ZETTELKASTEN_HTTP_CORS=false
ZETTELKASTEN_LOG_LEVEL=INFO
EOF

# Start with docker-compose
cd /path/to/zettelkasten-mcp
docker-compose -f docker/docker-compose.http.yml up -d

# Check logs
docker-compose -f docker/docker-compose.http.yml logs -f

# Test connection
curl http://localhost:8000/health
```

### Step 7: Update Claude Code Configuration

Connect Claude Code CLI to your new HTTP server:

```bash
# Remove old STDIO configuration (if applicable)
claude mcp remove zettelkasten

# Add new HTTP configuration
claude mcp add --transport http zettelkasten http://your-server:8000/mcp

# For remote server (if firewall allows)
claude mcp add --transport http zettelkasten http://192.168.1.100:8000/mcp
```

### Step 8: Keep STDIO for Claude Desktop (Dual Setup)

You can run both STDIO and HTTP simultaneously:

**Claude Desktop** (STDIO on demand):
Keep your existing `claude_desktop_config.json` unchanged.

**HTTP Server** (always running):
```bash
# Run HTTP on different port or different machine
python -m zettelkasten_mcp.main --transport http --port 8000
```

This way:
- Claude Desktop uses STDIO (local, secure)
- Claude Code CLI uses HTTP (remote access)

## Post-Migration Checklist

- [ ] HTTP server starts without errors
- [ ] Can connect with `claude mcp list`
- [ ] Can execute MCP commands successfully
- [ ] Notes and database accessible at correct paths
- [ ] Environment variables configured correctly
- [ ] (Optional) Systemd service running and enabled
- [ ] (Optional) Docker container healthy
- [ ] (Optional) Firewall rules configured
- [ ] (Optional) Reverse proxy set up for HTTPS
- [ ] (Optional) STDIO still works for Claude Desktop

## Rollback Plan

If you need to revert to STDIO only:

### Option 1: Stop HTTP Server
```bash
# If running manually
# Press Ctrl+C in server terminal

# If systemd service
sudo systemctl stop zettelkasten-mcp
sudo systemctl disable zettelkasten-mcp

# If Docker
docker-compose -f docker/docker-compose.http.yml down
```

### Option 2: Continue Using STDIO
STDIO transport still works (it's the default). Just run:
```bash
python -m zettelkasten_mcp.main
# or let Claude Desktop start it
```

No code changes needed - HTTP support is completely opt-in.

## Troubleshooting

See [Troubleshooting Guide](troubleshooting-http-transport.md) for common migration issues.

## Security Recommendations

After migrating to HTTP:

1. **Use HTTPS**: Set up reverse proxy with TLS
2. **Add Authentication**: Use nginx basic auth or OAuth
3. **Firewall Rules**: Restrict access to trusted IPs
4. **Monitor Logs**: Watch for unauthorized access attempts
5. **Regular Backups**: Back up notes and database
6. **Update Software**: Keep server and dependencies updated

## Next Steps

- Read [HTTP Usage Guide](../HTTP_USAGE.md) for advanced configuration
- Set up monitoring and alerting
- Configure automated backups
- Consider high availability setup (if critical)
```

---

