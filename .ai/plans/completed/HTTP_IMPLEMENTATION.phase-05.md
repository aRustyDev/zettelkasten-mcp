---
id: 47D1B4D4-353A-49FF-A138-3287202EE890
title: HTTP Transport Implementation - Phase 5: Documentation Updates
status: ✅ Completed
date: 2025-11-21
author: aRustyDev
---
# HTTP Transport Implementation - Phase 5: Documentation Updates

**Status:** ✅ COMPLETED
**Date:** 2025-11-21
**Commit:** abc52f5
**Plan:** [Back to main plan](../HTTP_IMPLEMENTATION.md)

---


### Step 5.1: Update README.md
**File:** `README.md`

**Action:** Add HTTP transport section to the README:

**Section to Add (after existing Installation/Configuration):**

```markdown
## Transport Options

Zettelkasten MCP supports two transport mechanisms:

### STDIO Transport (Default)

For use with Claude Desktop or other local MCP clients:

```json
{
  "mcpServers": {
    "zettelkasten": {
      "command": "/path/to/zettelkasten-mcp/.venv/bin/python",
      "args": ["-m", "zettelkasten_mcp"],
      "env": {
        "ZETTELKASTEN_ROOT": "/path/to/your/zettelkasten"
      }
    }
  }
}
```

### HTTP Transport

For remote access or browser-based clients:

**Start the server:**
```bash
python -m zettelkasten_mcp --transport http --port 8000
```

**Configure Claude Code:**
```bash
claude mcp add --transport http zettelkasten http://localhost:8000/mcp
```

**Environment Variables:**
```bash
export ZETTELKASTEN_HTTP_HOST=0.0.0.0
export ZETTELKASTEN_HTTP_PORT=8000
export ZETTELKASTEN_HTTP_CORS=true
export ZETTELKASTEN_ROOT=/path/to/your/zettelkasten
python -m zettelkasten_mcp --transport http
```

**CORS Support:**
For browser-based clients, enable CORS:
```bash
python -m zettelkasten_mcp --transport http --cors
```

Or via environment:
```bash
export ZETTELKASTEN_HTTP_CORS=true
export ZETTELKASTEN_HTTP_CORS_ORIGINS=https://example.com,https://app.example.com
```
```

### Step 5.2: Create HTTP_USAGE.md (Optional)
Create a dedicated guide for HTTP deployment scenarios.

---

