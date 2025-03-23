from typing import Optional

from fonny.ports.communication_port import CommunicationPort


class NullCommunicationAdapter(CommunicationPort):
    """
    A null implementation of the CommunicationPort interface.
    This adapter raises NotImplementedError for all methods.
    It serves as a placeholder until a real adapter is set.
    """
    
    def connect(self) -> bool:
        """
        Raise NotImplementedError.
        
        Returns:
            bool: Never returns, always raises an exception
        """
        raise NotImplementedError("No communication adapter has been set")
    
    def disconnect(self) -> None:
        """
        Raise NotImplementedError.
        """
        raise NotImplementedError("No communication adapter has been set")
    
    def send_command(self, command: str) -> None:
        """
        Raise NotImplementedError.
        
        Args:
            command: The command to send
        """
        raise NotImplementedError("No communication adapter has been set")
    
    def receive_response(self) -> Optional[str]:
        """
        Raise NotImplementedError.
        
        Returns:
            The response received or None if no response is available
        """
        raise NotImplementedError("No communication adapter has been set")
    
    def is_connected(self) -> bool:
        """
        Raise NotImplementedError.
        
        Returns:
            bool: Never returns, always raises an exception
        """
        raise NotImplementedError("No communication adapter has been set")
