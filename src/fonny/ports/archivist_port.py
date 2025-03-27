from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any


class EventType(Enum):
    """Types of events that can be archived."""
    USER_COMMAND = auto()
    SYSTEM_RESPONSE = auto()
    SYSTEM_ERROR = auto()
    CONNECTION_OPENED = auto()
    CONNECTION_CLOSED = auto()


class ArchivistPort(ABC):
    """
    Port interface for archiving events in the FORTH REPL system.
    Implementations of this interface can store events in different backends.
    """
    
    @abstractmethod
    def record_event(self, event_type: EventType, data: Dict[str, Any], timestamp: datetime) -> None:
        """
        Record an event with the specified type and data.
        
        Args:
            event_type: The type of event
            data: Additional data associated with the event
            timestamp: Timestamp for the event
        """
        pass
    
    def _record_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """
        Record an event with the current timestamp.
        
        Args:
            event_type: The type of event
            data: Additional data associated with the event
        """
        self.record_event(event_type, data, datetime.now())
    
    def record_user_command(self, command: str) -> None:
        """
        Record a command sent by the user.
        
        Args:
            command: The command sent by the user
        """
        self._record_event(
            EventType.USER_COMMAND,
            {
                "command": command
            }
        )
    
    def record_system_response(self, response: str) -> None:
        """
        Record a response received from the system.
        
        Args:
            response: The response received from the system
        """
        self._record_event(
            EventType.SYSTEM_RESPONSE,
            {
                "response": response
            }
        )
    
    def record_system_error(self, error: str) -> None:
        """
        Record an error that occurred in the system.
        
        Args:
            error: The error message
        """
        self._record_event(
            EventType.SYSTEM_ERROR,
            {
                "error": error
            }
        )
    
    def record_connection_opened(self) -> None:
        """Record that a _connection was opened."""
        self._record_event(
            EventType.CONNECTION_OPENED,
            {}
        )
    
    def record_connection_closed(self) -> None:
        """Record that a _connection was closed."""
        self._record_event(
            EventType.CONNECTION_CLOSED,
            {}
        )
