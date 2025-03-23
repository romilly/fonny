from abc import ABC, abstractmethod


class CharacterHandlerPort(ABC):
    """
    Abstract class for handling characters received from a communication port.
    This allows for real-time processing of characters as they arrive.
    """
    
    @abstractmethod
    def handle_character(self, char: str) -> None:
        """
        Handle a single character received from the communication port.
        
        Args:
            char: The character received
        """
        pass
