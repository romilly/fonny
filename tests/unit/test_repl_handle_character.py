"""
Unit tests for the handle_character method of the ForthRepl class.

These tests verify that the ForthRepl can correctly process characters
received from a communication port and record responses in archivists.
"""
import unittest
from datetime import datetime

from fonny.core.repl import ForthRepl
from fonny.adapters.null_adapter import NullCommunicationAdapter
from fonny.ports.archivist_port import ArchivistPort, EventType


class MockArchivist(ArchivistPort):
    """
    Test implementation of the ArchivistPort interface for testing.
    Records events in memory for later verification.
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


class TestForthReplHandleCharacter(unittest.TestCase):
    """Tests for the handle_character method of the ForthRepl class."""
    
    def setUp(self):
        """Set up a ForthRepl instance with a test archivist for testing."""
        self.repl = ForthRepl()
        self.test_archivist = MockArchivist()
        self.repl.add_archivist(self.test_archivist)
    
    def test_handle_character_processes_single_character(self):
        """Test that handle_character processes a single character."""
        # Send a single character
        self.repl.handle_character('A')
        
        # No response should be recorded yet (waiting for newline)
        self.assertEqual(len(self.test_archivist.system_responses), 0)
    
    def test_handle_character_processes_complete_line(self):
        """Test that handle_character processes a complete line ending with newline."""
        # Send a complete line character by character
        for char in "Hello, FORTH!\n":
            self.repl.handle_character(char)
        
        # A response should be recorded with the newline character stripped
        self.assertEqual(len(self.test_archivist.system_responses), 1)
        self.assertEqual(self.test_archivist.system_responses[0], "Hello, FORTH!")
    
    def test_handle_character_processes_multiple_lines(self):
        """Test that handle_character processes multiple lines."""
        # Send multiple lines character by character
        for char in "Line 1\nLine 2\nLine 3\n":
            self.repl.handle_character(char)
        
        # Each line should be recorded as a separate response with newline characters stripped
        self.assertEqual(len(self.test_archivist.system_responses), 3)
        self.assertEqual(self.test_archivist.system_responses[0], "Line 1")
        self.assertEqual(self.test_archivist.system_responses[1], "Line 2")
        self.assertEqual(self.test_archivist.system_responses[2], "Line 3")
    
    def test_handle_character_processes_carriage_return(self):
        """Test that handle_character processes lines ending with carriage return."""
        # Send a line ending with carriage return
        for char in "Hello, FORTH!\r":
            self.repl.handle_character(char)
        
        # A response should be recorded with the carriage return character stripped
        self.assertEqual(len(self.test_archivist.system_responses), 1)
        self.assertEqual(self.test_archivist.system_responses[0], "Hello, FORTH!")
    
    def test_handle_character_processes_carriage_return_newline(self):
        """Test that handle_character processes lines ending with carriage return and newline."""
        # Send a line ending with carriage return and newline
        for char in "Hello, FORTH!\r\n":
            self.repl.handle_character(char)
        
        # The response should be recorded once with both line ending characters stripped
        self.assertEqual(len(self.test_archivist.system_responses), 1)
        self.assertEqual(self.test_archivist.system_responses[0], "Hello, FORTH!")


if __name__ == '__main__':
    unittest.main()
