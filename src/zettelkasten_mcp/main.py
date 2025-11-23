#!/usr/bin/env python
"""Main entry point for the Zettelkasten MCP server."""

import argparse
import logging
import os
import sys
from pathlib import Path

from zettelkasten_mcp.config import config
from zettelkasten_mcp.models.db_models import init_db
from zettelkasten_mcp.server.mcp_server import ZettelkastenMcpServer
from zettelkasten_mcp.utils import setup_logging


def parse_args():
    """Parse command line arguments."""
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

  # Run with HTTP using environment variables
  ZETTELKASTEN_HTTP_PORT=9000 python -m zettelkasten_mcp --transport http
        """,
    )

    # Storage configuration
    parser.add_argument(
        "--notes-dir",
        help="Directory for storing note files",
        type=str,
        default=os.environ.get("ZETTELKASTEN_NOTES_DIR"),
    )
    parser.add_argument(
        "--database-path",
        help="SQLite database file path",
        type=str,
        default=os.environ.get("ZETTELKASTEN_DATABASE_PATH"),
    )

    # Logging configuration
    parser.add_argument(
        "--log-level",
        help="Logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.environ.get("ZETTELKASTEN_LOG_LEVEL", "INFO"),
    )

    # Transport configuration
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host",
        type=str,
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

    return parser.parse_args()


def update_config(args):
    """Update the global config with command line arguments."""
    if args.notes_dir:
        config.notes_dir = Path(args.notes_dir)
    if args.database_path:
        config.database_path = Path(args.database_path)


def main():
    """Run the Zettelkasten MCP server."""
    # Parse arguments and update config
    args = parse_args()
    update_config(args)

    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Ensure directories exist
    notes_dir = config.get_absolute_path(config.notes_dir)
    notes_dir.mkdir(parents=True, exist_ok=True)
    db_dir = config.get_absolute_path(config.database_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    # Initialize database schema
    try:
        logger.info(f"Using SQLite database: {config.get_db_url()}")
        init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    # Create and run the MCP server
    try:
        logger.info("Starting Zettelkasten MCP server")
        server = ZettelkastenMcpServer()
        server.run(
            transport=args.transport,
            host=args.host,
            port=args.port,
            enable_cors=args.cors,
        )
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
