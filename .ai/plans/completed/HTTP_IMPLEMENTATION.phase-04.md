# HTTP Transport Implementation - Phase 4: Update Entry Point

**Status:** ✅ COMPLETED
**Date:** 2025-11-20
**Commit:** f657484
**Plan:** [Back to main plan](../HTTP_IMPLEMENTATION.md)

---


### Step 4.1: Modify main.py
**File:** `src/zettelkasten_mcp/main.py`

**Current Code (approximate):**
```python
def main() -> None:
    """Main entry point for the MCP server."""
    server = ZettelkastenMcpServer()
    server.run()
```

**Updated Code:**
```python
import argparse
from zettelkasten_mcp.server.mcp_server import ZettelkastenMcpServer
from zettelkasten_mcp import config


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description="Zettelkasten MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with STDIO (default, for Claude Desktop)
  python -m zettelkasten_mcp

  # Run with HTTP transport
  python -m zettelkasten_mcp --transport http

  # Run with HTTP on custom port
  python -m zettelkasten_mcp --transport http --port 8080

  # Run with HTTP and CORS enabled
  python -m zettelkasten_mcp --transport http --cors
        """
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help=f"HTTP host to bind to (default: {config.http_host})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=f"HTTP port to bind to (default: {config.http_port})",
    )
    parser.add_argument(
        "--cors",
        action="store_true",
        default=None,
        help="Enable CORS for HTTP transport (default: from config)",
    )

    args = parser.parse_args()

    server = ZettelkastenMcpServer()
    server.run(
        transport=args.transport,
        host=args.host,
        port=args.port,
        enable_cors=args.cors,
    )


if __name__ == "__main__":
    main()
```

**Rationale:**
- CLI argument parsing for transport selection
- Comprehensive help text with examples
- Falls back to config defaults when arguments not provided
- Maintains simple default behavior (STDIO)

---

