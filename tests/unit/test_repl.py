import pytest
from unittest.mock import MagicMock, call

from fonny.ports.communication_port import CommunicationPort
from fonny.ports.archivist_port import ArchivistPort, EventType
from fonny.core.repl import ForthRepl
from datetime import datetime


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


class MockArchivist(ArchivistPort):
    """
    Mock implementation of the ArchivistPort interface for testing.
    """
    
    def __init__(self):
        self.events = []
    
    def record_event(self, event_type: EventType, data: dict, timestamp: datetime) -> None:
        """Record an event by storing it in a list."""
        self.events.append((event_type, data, timestamp))


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
    
    def test_archivists_record_responses(self):
        """Test that archivists record responses."""
        # Arrange
        mock_port = MockCommunicationPort(responses=["Response 1", "Response 2"])
        repl = ForthRepl(mock_port)
        repl.start()
        
        mock_archivist = MockArchivist()
        repl.add_archivist(mock_archivist)
        
        # Act
        repl.process_command("some command")
        
        # Assert
        # Check for user command event
        assert any(event[0] == EventType.USER_COMMAND and event[1]["command"] == "some command" for event in mock_archivist.events)
        
        # Check for system response events
        assert any(event[0] == EventType.SYSTEM_RESPONSE and event[1]["response"] == "Response 1" for event in mock_archivist.events)
        assert any(event[0] == EventType.SYSTEM_RESPONSE and event[1]["response"] == "Response 2" for event in mock_archivist.events)
    
    def test_remove_archivist(self):
        """Test that remove_archivist removes an archivist."""
        # Arrange
        mock_port = MockCommunicationPort(responses=["Response"])
        repl = ForthRepl(mock_port)
        repl.start()
        
        mock_archivist = MockArchivist()
        repl.add_archivist(mock_archivist)
        
        # Act
        repl.remove_archivist(mock_archivist)
        repl.process_command("some command")
        
        # Assert
        assert len(mock_archivist.events) == 0
    
    def test_archivists_record_connection_events(self):
        """Test that archivists record connection events."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl(mock_port)
        
        mock_archivist = MockArchivist()
        repl.add_archivist(mock_archivist)
        
        # Act
        repl.start()
        repl.stop()
        
        # Assert
        # Check for connection opened event
        assert any(event[0] == EventType.CONNECTION_OPENED for event in mock_archivist.events)
        
        # Check for connection closed event
        assert any(event[0] == EventType.CONNECTION_CLOSED for event in mock_archivist.events)
    
    def test_archivists_record_errors(self):
        """Test that archivists record errors."""
        # Arrange
        mock_port = MockCommunicationPort()
        mock_port.receive_response = MagicMock(side_effect=Exception("Test error"))
        
        repl = ForthRepl(mock_port)
        repl.start()
        
        mock_archivist = MockArchivist()
        repl.add_archivist(mock_archivist)
        
        # Act & Assert
        with pytest.raises(Exception):
            repl.process_command("command that will cause an error")
        
        # Check for error event
        assert any(event[0] == EventType.SYSTEM_ERROR and event[1]["error"] == "Test error" for event in mock_archivist.events)
