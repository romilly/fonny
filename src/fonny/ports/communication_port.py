from abc import ABC, abstractmethod
from typing import Optional


class CommunicationPort(ABC):
    """
    Port interface for communication with a FORTH system.
    This defines the boundary between the application core and external communication methods.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish a _connection to the FORTH system.
        
        Returns:
            bool: True if _connection was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the _connection to the FORTH system.
        """
        pass
    
    @abstractmethod
    def send_command(self, command: str) -> None:
        """
        Send a command to the FORTH system.
        
        Args:
            command: The command to send
        """
        pass

    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the _connection is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        pass
