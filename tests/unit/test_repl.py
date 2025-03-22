import pytest
from unittest.mock import MagicMock, call

from fonny.ports.communication_port import CommunicationPort
from fonny.core.repl import ForthRepl


class MockCommunicationPort(CommunicationPort):
    """
    Mock implementation of the CommunicationPort interface for testing.
    """
    
    def __init__(self, responses=None):
        """
        Initialize the mock with optional predefined responses.
        
        Args:
            responses: List of responses to return when receive_response is called
        """
        self.connected = False
        self.commands = []
        self.responses = responses or []
        self.response_index = 0
    
    def connect(self) -> bool:
        """Mock implementation of connect."""
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        """Mock implementation of disconnect."""
        self.connected = False
    
    def send_command(self, command: str) -> None:
        """Mock implementation of send_command."""
        if not self.connected:
            raise ConnectionError("Not connected")
        self.commands.append(command)
    
    def receive_response(self) -> str:
        """Mock implementation of receive_response."""
        if not self.connected:
            raise ConnectionError("Not connected")
        
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            return response
        
        return None
    
    def is_connected(self) -> bool:
        """Mock implementation of is_connected."""
        return self.connected


class TestForthRepl:
    """Tests for the ForthRepl class."""
    
    def test_start_connects_to_port(self):
        """Test that start method connects to the communication port."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl(mock_port)
        
        # Act
        result = repl.start()
        
        # Assert
        assert result is True
        assert mock_port.connected is True
    
    def test_stop_disconnects_from_port(self):
        """Test that stop method disconnects from the communication port."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl(mock_port)
        repl.start()
        
        # Act
        repl.stop()
        
        # Assert
        assert mock_port.connected is False
    
    def test_process_command_sends_to_port(self):
        """Test that process_command sends the command to the port."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl(mock_port)
        repl.start()
        
        # Act
        repl.process_command("2 2 +")
        
        # Assert
        assert mock_port.commands == ["2 2 +\n"]
    
    def test_process_command_adds_newline_if_missing(self):
        """Test that process_command adds a newline if it's missing."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl(mock_port)
        repl.start()
        
        # Act
        repl.process_command("2 2 +")
        repl.process_command("3 3 +\n")
        
        # Assert
        assert mock_port.commands == ["2 2 +\n", "3 3 +\n"]
    
    def test_process_command_handles_exit_command(self):
        """Test that process_command handles the exit command."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl(mock_port)
        repl.start()
        
        # Act
        repl.process_command("exit")
        
        # Assert
        assert mock_port.commands == []  # No command should be sent
    
    def test_response_handlers_are_called(self):
        """Test that response handlers are called with responses."""
        # Arrange
        mock_port = MockCommunicationPort(responses=["Response 1", "Response 2"])
        repl = ForthRepl(mock_port)
        repl.start()
        
        mock_handler = MagicMock()
        repl.add_response_handler(mock_handler)
        
        # Act
        repl.process_command("some command")
        
        # Assert
        assert mock_handler.call_count == 2
        mock_handler.assert_has_calls([
            call("Response 1"),
            call("Response 2")
        ])
    
    def test_remove_response_handler(self):
        """Test that remove_response_handler removes a handler."""
        # Arrange
        mock_port = MockCommunicationPort(responses=["Response"])
        repl = ForthRepl(mock_port)
        repl.start()
        
        mock_handler = MagicMock()
        repl.add_response_handler(mock_handler)
        
        # Act
        repl.remove_response_handler(mock_handler)
        repl.process_command("some command")
        
        # Assert
        mock_handler.assert_not_called()
