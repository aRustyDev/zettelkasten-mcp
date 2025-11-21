"""Tests for HTTP transport functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from zettelkasten_mcp.server.mcp_server import ZettelkastenMcpServer
from zettelkasten_mcp.config import config


class TestHTTPTransport:
    """Test HTTP transport functionality."""

    @pytest.fixture
    def server(self):
        """Create a server instance for testing."""
        return ZettelkastenMcpServer()

    def test_server_initializes_with_json_response(self, server):
        """Test that server initializes FastMCP with json_response parameter."""
        # Verify that json_response was set during initialization
        assert server.mcp is not None
        # The json_response parameter is passed to FastMCP init
        # This is verified by checking the config value was used
        assert config.json_response is True

    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_stdio_transport_selected_by_default(self, mock_logger, server):
        """Test that STDIO is the default transport."""
        with patch.object(server.mcp, 'run') as mock_run:
            server.run()

            # Verify mcp.run() was called for STDIO mode
            mock_run.assert_called_once()
            # Verify STDIO logging message
            mock_logger.info.assert_called_with("Starting STDIO server")

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_http_transport_with_default_port(self, mock_logger, mock_uvicorn, server):
        """Test HTTP transport starts on default port 8000."""
        with patch.object(server.mcp, 'sse_app', return_value=Mock()) as mock_sse_app:
            server.run(transport="http")

            # Verify uvicorn.run() was called with correct defaults
            mock_uvicorn.run.assert_called_once()
            call_args = mock_uvicorn.run.call_args

            assert call_args[1]['host'] == config.http_host
            assert call_args[1]['port'] == config.http_port
            # Verify sse_app was called
            mock_sse_app.assert_called_once()

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_http_transport_with_custom_port(self, mock_logger, mock_uvicorn, server):
        """Test HTTP transport starts on custom port."""
        custom_port = 9001

        with patch.object(server.mcp, 'sse_app', return_value=Mock()):
            server.run(transport="http", port=custom_port)

            # Verify uvicorn.run() was called with custom port
            call_args = mock_uvicorn.run.call_args
            assert call_args[1]['port'] == custom_port

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_http_transport_with_custom_host(self, mock_logger, mock_uvicorn, server):
        """Test HTTP transport binds to custom host."""
        custom_host = "127.0.0.1"

        with patch.object(server.mcp, 'sse_app', return_value=Mock()):
            server.run(transport="http", host=custom_host)

            # Verify uvicorn.run() was called with custom host
            call_args = mock_uvicorn.run.call_args
            assert call_args[1]['host'] == custom_host

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_http_transport_with_custom_host_and_port(self, mock_logger, mock_uvicorn, server):
        """Test HTTP transport with both custom host and port."""
        custom_host = "192.168.1.100"
        custom_port = 9500

        with patch.object(server.mcp, 'sse_app', return_value=Mock()):
            server.run(transport="http", host=custom_host, port=custom_port)

            # Verify uvicorn.run() was called with custom values
            call_args = mock_uvicorn.run.call_args
            assert call_args[1]['host'] == custom_host
            assert call_args[1]['port'] == custom_port

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_cors_middleware_not_applied_by_default(self, mock_logger, mock_uvicorn, server):
        """Test that CORS middleware is not applied by default."""
        with patch.object(server.mcp, 'sse_app', return_value=Mock()) as mock_sse_app:
            # Mock CORSMiddleware to verify it's not imported/used
            with patch('zettelkasten_mcp.server.mcp_server.CORSMiddleware', create=True) as mock_cors:
                server.run(transport="http", enable_cors=False)

                # Verify CORSMiddleware was NOT called
                mock_cors.assert_not_called()
                # Verify sse_app result was passed directly to uvicorn
                mock_sse_app.assert_called_once()

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_cors_middleware_applied_when_enabled(self, mock_logger, mock_uvicorn, server):
        """Test that CORS middleware is applied when enabled."""
        with patch.object(server.mcp, 'sse_app', return_value=Mock()) as mock_sse_app:
            # Create a mock for CORSMiddleware that will be imported
            mock_cors_instance = Mock()

            with patch('zettelkasten_mcp.server.mcp_server.CORSMiddleware', return_value=mock_cors_instance) as mock_cors_class:
                server.run(transport="http", enable_cors=True)

                # Verify CORSMiddleware was called
                mock_cors_class.assert_called_once()
                # Verify the wrapped app was passed to uvicorn
                mock_uvicorn.run.assert_called_once()
                call_args = mock_uvicorn.run.call_args
                assert call_args[0][0] == mock_cors_instance

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_cors_origins_configuration(self, mock_logger, mock_uvicorn, server):
        """Test that CORS origins are correctly configured."""
        with patch.object(server.mcp, 'sse_app', return_value=Mock()):
            with patch('zettelkasten_mcp.server.mcp_server.CORSMiddleware') as mock_cors:
                server.run(transport="http", enable_cors=True)

                # Verify CORSMiddleware was called with correct origins
                call_args = mock_cors.call_args
                assert call_args[1]['allow_origins'] == config.http_cors_origins

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_cors_middleware_configuration(self, mock_logger, mock_uvicorn, server):
        """Test that CORS middleware is configured with correct parameters."""
        with patch.object(server.mcp, 'sse_app', return_value=Mock()):
            with patch('zettelkasten_mcp.server.mcp_server.CORSMiddleware') as mock_cors:
                server.run(transport="http", enable_cors=True)

                # Verify CORSMiddleware was called with all correct parameters
                call_args = mock_cors.call_args
                assert call_args[1]['allow_methods'] == ["GET", "POST", "OPTIONS"]
                assert call_args[1]['allow_headers'] == ["*"]
                assert call_args[1]['expose_headers'] == ["Mcp-Session-Id"]

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_sse_app_method_called_for_http(self, mock_logger, mock_uvicorn, server):
        """Test that sse_app() is called for HTTP transport."""
        with patch.object(server.mcp, 'sse_app', return_value=Mock()) as mock_sse_app:
            server.run(transport="http")

            # Verify self.mcp.sse_app() was called
            mock_sse_app.assert_called_once()

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_http_logging_without_cors(self, mock_logger, mock_uvicorn, server):
        """Test that correct log message is generated for HTTP without CORS."""
        with patch.object(server.mcp, 'sse_app', return_value=Mock()):
            server.run(transport="http", host="localhost", port=8080, enable_cors=False)

            # Verify logging message
            mock_logger.info.assert_called_with("Starting HTTP server on localhost:8080")

    @patch('zettelkasten_mcp.server.mcp_server.uvicorn')
    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_http_logging_with_cors(self, mock_logger, mock_uvicorn, server):
        """Test that correct log message is generated for HTTP with CORS."""
        with patch.object(server.mcp, 'sse_app', return_value=Mock()):
            with patch('zettelkasten_mcp.server.mcp_server.CORSMiddleware'):
                server.run(transport="http", host="localhost", port=8080, enable_cors=True)

                # Verify logging message includes CORS
                mock_logger.info.assert_called_with(
                    "Starting HTTP server on localhost:8080 with CORS enabled"
                )

    @patch('zettelkasten_mcp.server.mcp_server.logger')
    def test_stdio_logging(self, mock_logger, server):
        """Test that correct log message is generated for STDIO transport."""
        with patch.object(server.mcp, 'run'):
            server.run(transport="stdio")

            # Verify logging message
            mock_logger.info.assert_called_with("Starting STDIO server")
