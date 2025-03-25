import pytest
from unittest.mock import MagicMock, call
import unittest
from typing import List, Optional

from fonny.ports.communication_port import CommunicationPort
from fonny.ports.character_handler_port import CharacterHandlerPort
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


class MockCommunicationPortWithError(CommunicationPort):
    """
    Mock implementation of the CommunicationPort interface that raises an error on connect.
    """
    
    def __init__(self, error_message="Connection error"):
        """
        Initialize the mock with an error message.
        
        Args:
            error_message: The error message to raise when connect is called
        """
        self.connected = False
        self.commands = []
        self.error_message = error_message
    
    def connect(self) -> bool:
        """Mock implementation of connect that raises an exception."""
        raise Exception(self.error_message)
    
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
        return None
    
    def is_connected(self) -> bool:
        """Mock implementation of is_connected."""
        return self.connected


class MockCharacterHandler(CharacterHandlerPort):
    """
    Mock implementation of the CharacterHandlerPort interface for testing.
    """
    
    def __init__(self):
        self.received_chars: List[str] = []
        
    def handle_character(self, char: str) -> None:
        """
        Handle a single character by adding it to the received_chars list.
        
        Args:
            char: The character received
        """
        self.received_chars.append(char)
        
    def get_received_text(self) -> str:
        """
        Get the complete text received so far.
        
        Returns:
            str: The concatenated received characters
        """
        return ''.join(self.received_chars)


class MockCommunicationPortWithCharacterHandler(CommunicationPort):
    """
    Mock implementation of the CommunicationPort interface that supports
    character-by-character reading for testing.
    """
    
    def __init__(self, character_handler: CharacterHandlerPort, responses=None):
        """
        Initialize the mock with a character handler and optional predefined responses.
        
        Args:
            character_handler: Handler for processing characters as they arrive
            responses: List of responses to return when receive_response is called
        """
        self.connected = False
        self.commands = []
        self.responses = responses or []
        self.response_index = 0
        self._character_handler = character_handler
    
    def connect(self) -> bool:
        """Mock implementation of connect."""
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        """Mock implementation of disconnect."""
        self.connected = False
    
    def send_command(self, command: str) -> None:
        """
        Mock implementation of send_command.
        
        This implementation simulates sending a command and then immediately
        processes the response character by character.
        """
        if not self.connected:
            raise ConnectionError("Not connected")
        
        self.commands.append(command)
        
        # Simulate character-by-character response processing
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            
            # Process each character in the response
            for char in response:
                if self._character_handler:
                    self._character_handler.handle_character(char)
    
    def receive_response(self) -> Optional[str]:
        """
        Mock implementation of receive_response.
        
        This method is maintained for backward compatibility.
        When using a character handler, responses are processed
        character by character in real-time.
        """
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
        
    def clear_buffer(self) -> None:
        """Mock implementation of clear_buffer."""
        pass


class MockArchivist(ArchivistPort):
    """
    Mock implementation of the ArchivistPort interface for testing.
    """
    
    def __init__(self):
        self.events = []
        self.system_responses = []
    
    def record_event(self, event_type: EventType, data: dict, timestamp: datetime) -> None:
        """Record an event by storing it in a list."""
        self.events.append((event_type, data, timestamp))
        
    def record_user_command(self, command: str) -> None:
        """Record a user command."""
        self.record_event(EventType.USER_COMMAND, {"command": command}, datetime.now())
    
    def record_system_response(self, response: str) -> None:
        """Record a system response."""
        self.system_responses.append(response)
        self.record_event(EventType.SYSTEM_RESPONSE, {"response": response}, datetime.now())
    
    def record_system_error(self, error: str) -> None:
        """Record a system error."""
        self.record_event(EventType.SYSTEM_ERROR, {"error": error}, datetime.now())
    
    def record_connection_opened(self) -> None:
        """Record a connection opened event."""
        self.record_event(EventType.CONNECTION_OPENED, {}, datetime.now())
    
    def record_connection_closed(self) -> None:
        """Record a connection closed event."""
        self.record_event(EventType.CONNECTION_CLOSED, {}, datetime.now())


class TestForthRepl:
    """Tests for the ForthRepl class."""
    
    def test_start_connects_to_port(self):
        """Test that start method connects to the communication port."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl()
        repl.set_communication_port(mock_port)
        
        # Act
        result = repl.start()
        
        # Assert
        assert result is True
        assert mock_port.connected is True
    
    def test_stop_disconnects_from_port(self):
        """Test that stop method disconnects from the communication port."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl()
        repl.set_communication_port(mock_port)
        repl.start()
        
        # Act
        repl.stop()
        
        # Assert
        assert mock_port.connected is False
    
    def test_process_command_sends_to_port(self):
        """Test that process_command sends the command to the port."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl()
        repl.set_communication_port(mock_port)
        repl.start()
        
        # Act
        repl.process_command("2 2 +")
        
        # Assert
        assert mock_port.commands == ["2 2 +\n"]
    
    def test_process_command_adds_newline_if_missing(self):
        """Test that process_command adds a newline if it's missing."""
        # Arrange
        mock_port = MockCommunicationPort()
        repl = ForthRepl()
        repl.set_communication_port(mock_port)
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
        repl = ForthRepl()
        repl.set_communication_port(mock_port)
        repl.start()
        
        # Act
        repl.process_command("exit")
        
        # Assert
        assert mock_port.commands == []  # No command should be sent
    
    def test_archivists_record_responses(self):
        """Test that archivists record responses."""
        # Arrange
        mock_port = MockCommunicationPort()
        mock_archivist = MockArchivist()
        repl = ForthRepl(mock_archivist)
        repl.set_communication_port(mock_port)
        repl.start()
        
        # Act
        repl.process_command("some command")
        
        # Simulate receiving characters directly via the character handler
        repl.handle_character('R')
        repl.handle_character('e')
        repl.handle_character('s')
        repl.handle_character('p')
        repl.handle_character('o')
        repl.handle_character('n')
        repl.handle_character('s')
        repl.handle_character('e')
        repl.handle_character(' ')
        repl.handle_character('1')
        repl.handle_character('\n')
        
        repl.handle_character('R')
        repl.handle_character('e')
        repl.handle_character('s')
        repl.handle_character('p')
        repl.handle_character('o')
        repl.handle_character('n')
        repl.handle_character('s')
        repl.handle_character('e')
        repl.handle_character(' ')
        repl.handle_character('2')
        repl.handle_character('\n')
        
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
        mock_archivist = MockArchivist()
        repl = ForthRepl(mock_archivist)
        repl.set_communication_port(mock_port)
        repl.start()
        
        # Clear any events recorded during setup
        mock_archivist.events.clear()
        
        # Act
        repl.remove_archivist(mock_archivist)
        repl.process_command("some command")
        
        # Assert
        assert len(mock_archivist.events) == 0
    
    def test_archivists_record_connection_events(self):
        """Test that archivists record connection events."""
        # Arrange
        mock_port = MockCommunicationPort()
        mock_archivist = MockArchivist()
        repl = ForthRepl(mock_archivist)
        repl.set_communication_port(mock_port)
        
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
        mock_port = MockCommunicationPortWithError("Connection error")
        mock_archivist = MockArchivist()
        repl = ForthRepl(mock_archivist)
        repl.set_communication_port(mock_port)
        
        # Act
        result = repl.start()
        
        # Assert
        assert result is False  # Connection should fail
        assert any(event[0] == EventType.SYSTEM_ERROR and "Connection error" in event[1]["error"] for event in mock_archivist.events)

    
    def test_handle_character_processes_single_character(self):
        """Test that handle_character processes a single character."""
        # Arrange
        mock_archivist = MockArchivist()
        repl = ForthRepl(mock_archivist)
        
        # Act
        repl.handle_character('A')
        
        # Assert
        assert len(mock_archivist.system_responses) == 0
    
    def test_handle_character_processes_complete_line(self):
        """Test that handle_character processes a complete line ending with newline."""
        # Arrange
        mock_archivist = MockArchivist()
        repl = ForthRepl(mock_archivist)
        
        # Act
        for char in "Hello, FORTH!\n":
            repl.handle_character(char)
        
        # Assert
        assert len(mock_archivist.system_responses) == 1
        assert mock_archivist.system_responses[0] == "Hello, FORTH!"
    
    def test_handle_character_processes_multiple_lines(self):
        """Test that handle_character processes multiple lines."""
        # Arrange
        mock_archivist = MockArchivist()
        repl = ForthRepl(mock_archivist)
        
        # Act
        for char in "Line 1\nLine 2\nLine 3\n":
            repl.handle_character(char)
        
        # Assert
        assert len(mock_archivist.system_responses) == 3
        assert mock_archivist.system_responses[0] == "Line 1"
        assert mock_archivist.system_responses[1] == "Line 2"
        assert mock_archivist.system_responses[2] == "Line 3"
    
    def test_handle_character_processes_carriage_return(self):
        """Test that handle_character processes lines ending with carriage return."""
        # Arrange
        mock_archivist = MockArchivist()
        repl = ForthRepl(mock_archivist)
        
        # Act
        for char in "Hello, FORTH!\r":
            repl.handle_character(char)
        
        # Assert
        assert len(mock_archivist.system_responses) == 1
        assert mock_archivist.system_responses[0] == "Hello, FORTH!"
    
    def test_handle_character_processes_carriage_return_newline(self):
        """Test that handle_character processes lines ending with carriage return and newline."""
        # Arrange
        mock_archivist = MockArchivist()
        repl = ForthRepl(mock_archivist)
        
        # Act
        for char in "Hello, FORTH!\r\n":
            repl.handle_character(char)
        
        # Assert
        assert len(mock_archivist.system_responses) == 1
        assert mock_archivist.system_responses[0] == "Hello, FORTH!"
    
    def test_archivist_records_connection_events(self):
        """Test that archivists record connection events."""
        # Arrange
        mock_port = MockCommunicationPort()
        test_archivist = MockArchivist()
        repl = ForthRepl(test_archivist)
        repl.set_communication_port(mock_port)
        
        # Act
        repl.start()
        repl.stop()
        
        # Assert
        # Check for connection opened event
        assert any(event[0] == EventType.CONNECTION_OPENED for event in test_archivist.events)
        # Check for connection closed event
        assert any(event[0] == EventType.CONNECTION_CLOSED for event in test_archivist.events)
    
    def test_archivist_records_user_commands(self):
        """Test that archivists record user commands."""
        # Arrange
        mock_port = MockCommunicationPort()
        test_archivist = MockArchivist()
        repl = ForthRepl(test_archivist)
        repl.set_communication_port(mock_port)
        repl.start()
        
        # Act
        repl.process_command("test command")
        
        # Assert
        assert any(event[0] == EventType.USER_COMMAND and event[1]["command"] == "test command" for event in test_archivist.events)
    
    def test_archivist_records_system_responses(self):
        """Test that archivists record system responses."""
        # Arrange
        mock_port = MockCommunicationPort()
        test_archivist = MockArchivist()
        repl = ForthRepl(test_archivist)
        repl.set_communication_port(mock_port)
        repl.start()
        
        # Act
        repl.process_command("test command")
        
        # Simulate receiving a response character by character
        for char in "test response\n":
            repl.handle_character(char)
        
        # Assert
        assert any(event[0] == EventType.SYSTEM_RESPONSE and event[1]["response"] == "test response" for event in test_archivist.events)
    
    def test_archivist_records_system_errors(self):
        """Test that archivists record system errors."""
        # Arrange
        mock_port = MockCommunicationPortWithError("Connection error")
        test_archivist = MockArchivist()
        repl = ForthRepl(test_archivist)
        repl.set_communication_port(mock_port)
        repl.start()
        
        # Act & Assert
        with pytest.raises(Exception):
            repl.process_command("test command")
        
        # Assert
        assert any(event[0] == EventType.SYSTEM_ERROR for event in test_archivist.events)
