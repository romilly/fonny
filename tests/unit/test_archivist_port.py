from typing import Dict, Any
from datetime import datetime

from fonny.ports.archivist_port import ArchivistPort, EventType


class MockArchivist(ArchivistPort):
    """Mock implementation of ArchivistPort for testing."""

    def __init__(self):
        self.events = []

    def record_event(self, event_type: EventType, data: Dict[str, Any], timestamp: datetime) -> None:
        """Record an event by storing it in a list."""
        self.events.append((event_type, data, timestamp))

    def close(self) -> None:
        pass


class TestArchivistPort:
    """Tests for the ArchivistPort interface."""
    
    def test_record_user_command(self):
        """Test that record_user_command calls record_event with the right parameters."""
        # Arrange
        archivist = MockArchivist()
        
        # Act
        archivist.record_user_command("test command")
        
        # Assert
        assert len(archivist.events) == 1
        event_type, data, timestamp = archivist.events[0]
        assert event_type == EventType.USER_COMMAND
        assert data["command"] == "test command"
        assert isinstance(timestamp, datetime)
    
    def test_record_system_response(self):
        """Test that record_system_response calls record_event with the right parameters."""
        # Arrange
        archivist = MockArchivist()
        
        # Act
        archivist.record_system_response("test response")
        
        # Assert
        assert len(archivist.events) == 1
        event_type, data, timestamp = archivist.events[0]
        assert event_type == EventType.SYSTEM_RESPONSE
        assert data["response"] == "test response"
        assert isinstance(timestamp, datetime)
    
    def test_record_system_error(self):
        """Test that record_system_error calls record_event with the right parameters."""
        # Arrange
        archivist = MockArchivist()
        
        # Act
        archivist.record_system_error("test error")
        
        # Assert
        assert len(archivist.events) == 1
        event_type, data, timestamp = archivist.events[0]
        assert event_type == EventType.SYSTEM_ERROR
        assert data["error"] == "test error"
        assert isinstance(timestamp, datetime)
    
    def test_record_connection_opened(self):
        """Test that record_connection_opened calls record_event with the right parameters."""
        # Arrange
        archivist = MockArchivist()
        
        # Act
        archivist.record_connection_opened()
        
        # Assert
        assert len(archivist.events) == 1
        event_type, data, timestamp = archivist.events[0]
        assert event_type == EventType.CONNECTION_OPENED
        assert data == {}
        assert isinstance(timestamp, datetime)
    
    def test_record_connection_closed(self):
        """Test that record_connection_closed calls record_event with the right parameters."""
        # Arrange
        archivist = MockArchivist()
        
        # Act
        archivist.record_connection_closed()
        
        # Assert
        assert len(archivist.events) == 1
        event_type, data, timestamp = archivist.events[0]
        assert event_type == EventType.CONNECTION_CLOSED
        assert data == {}
        assert isinstance(timestamp, datetime)
