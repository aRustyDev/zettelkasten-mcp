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
