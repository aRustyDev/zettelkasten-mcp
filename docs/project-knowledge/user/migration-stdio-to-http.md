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
