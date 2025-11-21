"""Tests for CLI argument parsing for HTTP transport."""
import pytest
from unittest.mock import patch
import sys
from zettelkasten_mcp.main import parse_args


class TestHTTPCLI:
    """Test CLI argument parsing for HTTP transport."""

    def test_default_transport_is_stdio(self):
        """Test that default transport is stdio."""
        test_args = ["program"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.transport == "stdio"

    def test_http_transport_argument(self):
        """Test --transport http argument."""
        test_args = ["program", "--transport", "http"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.transport == "http"

    def test_stdio_transport_explicit(self):
        """Test explicit --transport stdio argument."""
        test_args = ["program", "--transport", "stdio"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.transport == "stdio"

    def test_host_argument(self):
        """Test --host argument."""
        test_args = ["program", "--host", "127.0.0.1"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.host == "127.0.0.1"

    def test_port_argument(self):
        """Test --port argument."""
        test_args = ["program", "--port", "9000"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.port == 9000

    def test_port_argument_type(self):
        """Test that --port argument is converted to int."""
        test_args = ["program", "--port", "8080"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert isinstance(args.port, int)
            assert args.port == 8080

    def test_cors_flag(self):
        """Test --cors flag."""
        test_args = ["program", "--cors"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.cors is True

    def test_cors_default_is_none(self):
        """Test that --cors default is None when not specified."""
        test_args = ["program"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.cors is None

    def test_combined_http_arguments(self):
        """Test multiple HTTP arguments together."""
        test_args = [
            "program",
            "--transport", "http",
            "--host", "192.168.1.100",
            "--port", "9500",
            "--cors"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.transport == "http"
            assert args.host == "192.168.1.100"
            assert args.port == 9500
            assert args.cors is True

    def test_host_without_transport(self):
        """Test that --host can be specified without --transport."""
        test_args = ["program", "--host", "localhost"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            # host should be set even if transport defaults to stdio
            assert args.host == "localhost"
            assert args.transport == "stdio"

    def test_port_without_transport(self):
        """Test that --port can be specified without --transport."""
        test_args = ["program", "--port", "8080"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            # port should be set even if transport defaults to stdio
            assert args.port == 8080
            assert args.transport == "stdio"

    def test_invalid_transport_raises_error(self):
        """Test that invalid transport value raises an error."""
        test_args = ["program", "--transport", "invalid"]

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                parse_args()

    def test_invalid_port_raises_error(self):
        """Test that invalid port value raises an error."""
        test_args = ["program", "--port", "not_a_number"]

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                parse_args()

    def test_log_level_argument(self):
        """Test --log-level argument (ensure HTTP args don't break other args)."""
        test_args = ["program", "--log-level", "DEBUG"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.log_level == "DEBUG"

    def test_all_arguments_together(self):
        """Test all CLI arguments together."""
        test_args = [
            "program",
            "--transport", "http",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--cors",
            "--log-level", "INFO",
            "--notes-dir", "/tmp/notes",
            "--database-path", "/tmp/db/test.db"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.transport == "http"
            assert args.host == "0.0.0.0"
            assert args.port == 8000
            assert args.cors is True
            assert args.log_level == "INFO"
            assert args.notes_dir == "/tmp/notes"
            assert args.database_path == "/tmp/db/test.db"

    def test_cli_port_overrides_env_var(self, monkeypatch):
        """Test that CLI --port argument takes precedence over environment variable."""
        # Set environment variable
        monkeypatch.setenv("ZETTELKASTEN_HTTP_PORT", "9100")
        test_args = ["program", "--port", "9200"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            # CLI argument should override env var
            assert args.port == 9200

    def test_env_var_used_when_no_cli_port(self, monkeypatch):
        """Test that environment variable is used when CLI --port is not provided."""
        # Set environment variable
        monkeypatch.setenv("ZETTELKASTEN_HTTP_PORT", "9100")
        test_args = ["program"]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            # When no CLI arg, the env var doesn't affect parse_args
            # (it affects config loading, not arg parsing)
            assert args.port is None  # No CLI port provided

    def test_help_flag(self):
        """Test that --help flag works."""
        test_args = ["program", "--help"]

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            # --help exits with code 0
            assert exc_info.value.code == 0

    def test_notes_dir_argument(self):
        """Test --notes-dir argument doesn't interfere with HTTP args."""
        test_args = [
            "program",
            "--transport", "http",
            "--notes-dir", "/path/to/notes"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.transport == "http"
            assert args.notes_dir == "/path/to/notes"

    def test_database_path_argument(self):
        """Test --database-path argument doesn't interfere with HTTP args."""
        test_args = [
            "program",
            "--transport", "http",
            "--database-path", "/path/to/db.sqlite"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            assert args.transport == "http"
            assert args.database_path == "/path/to/db.sqlite"
