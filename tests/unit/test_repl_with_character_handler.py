import pytest
from typing import List, Optional

from fonny.ports.communication_port import CommunicationPort
from fonny.ports.character_handler_port import CharacterHandlerPort
from fonny.ports.archivist_port import ArchivistPort, EventType
from fonny.core.repl import ForthRepl
from datetime import datetime


class _MockCharacterHandler(CharacterHandlerPort):
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
    
    def record_event(self, event_type: EventType, data: dict, timestamp: datetime) -> None:
        """Record an event by storing it in a list."""
        self.events.append((event_type, data, timestamp))
    
    def record_user_command(self, command: str) -> None:
        """Record a user command."""
        self.record_event(EventType.USER_COMMAND, {"command": command}, datetime.now())
    
    def record_system_response(self, response: str) -> None:
        """Record a system response."""
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


class TestForthReplWithCharacterHandler:
    """Tests for the ForthRepl class with character-by-character reading."""
    
    def test_process_command_with_character_handler(self):
        """
        Test that process_command works with a communication port that
        supports character-by-character reading.
        """
        # Create a character handler
        char_handler = _MockCharacterHandler()
        
        # Create a mock communication port with the character handler
        responses = ["Hello, FORTH!\nok\n"]
        mock_port = MockCommunicationPortWithCharacterHandler(
            character_handler=char_handler,
            responses=responses
        )
        
        # Create a REPL with the mock port
        repl = ForthRepl(communication_port=mock_port)
        
        # Process a command
        repl.start()
        repl.process_command("test command")
        
        # Verify that the command was sent
        assert len(mock_port.commands) == 1
        assert mock_port.commands[0] == "test command\n"
        
        # Verify that characters were received
        assert len(char_handler.received_chars) > 0
        assert char_handler.get_received_text() == "Hello, FORTH!\nok\n"
    
    def test_archivists_record_responses_with_character_handler(self):
        """
        Test that archivists record responses when using a communication port
        that supports character-by-character reading.
        """
        # Create a character handler
        char_handler = _MockCharacterHandler()
        
        # Create a mock communication port with the character handler
        responses = ["Response 1\nok\n", "Response 2\nok\n"]
        mock_port = MockCommunicationPortWithCharacterHandler(
            character_handler=char_handler,
            responses=responses
        )
        
        # Create a mock archivist
        mock_archivist = MockArchivist()
        
        # Create a REPL with the mock port and add the archivist
        repl = ForthRepl(communication_port=mock_port)
        repl.add_archivist(mock_archivist)
        
        # Process a command
        repl.start()
        repl.process_command("test command")
        
        # Verify that the archivist recorded the command and responses
        assert len(mock_archivist.events) >= 2  # At least connection opened and command
        
        # Find the command event
        command_events = [e for e in mock_archivist.events if e[0] == EventType.USER_COMMAND]
        assert len(command_events) == 1
        assert command_events[0][1]["command"] == "test command"
        
        # Verify that characters were received
        assert len(char_handler.received_chars) > 0
        assert "Response 1" in char_handler.get_received_text()
        assert "ok" in char_handler.get_received_text()
