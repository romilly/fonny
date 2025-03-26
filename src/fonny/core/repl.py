from typing import Optional, List
from queue import Queue, Empty
from fonny.ports.communication_port import CommunicationPort
from fonny.ports.archivist_port import ArchivistPort
from fonny.adapters.null_adapter import NullCommunicationAdapter
from fonny.ports.character_handler_port import CharacterHandlerPort


class ForthRepl(CharacterHandlerPort):
    """
    Core REPL (Read-Eval-Print Loop) for interacting with a FORTH system.
    This class uses a CommunicationPort to send commands and receive responses.
    """
    
    def __init__(self, *archivists):
        """
        Initialize the REPL with a communication port.
        
        Args:
            *archivists: Optional archivists to add during initialization
        """
        self._comm_port = NullCommunicationAdapter()
        self._archivists = archivists
        self._current_response = ""
        self.character_queue = Queue()
    
    def set_communication_port(self, communication_port: CommunicationPort) -> None:
        self._comm_port = communication_port
    
    def handle_character(self, char: str) -> None:
        self.character_queue.put(char)
        # If we have a complete line (newline or carriage return), process it
        if char == '\n' or char == '\r':
            if self._current_response:  # Only process if we have content
                self._process_response(self._current_response)
                self._current_response = ""
        else:
            self._current_response += char
    
    def start(self) -> bool:
        try:
            success = self._comm_port.connect()
            if success:
                for archivist in self._archivists:
                    archivist.record_connection_opened()
            return success
        except Exception as e:
            for archivist in self._archivists:
                archivist.record_system_error(str(e))
            return False
    
    def stop(self) -> None:
        if self._comm_port.is_connected():
            for archivist in self._archivists:
                archivist.record_connection_closed()
            self._comm_port.disconnect()
    
    def process_command(self, command: str) -> None:
        if command.lower() == 'exit':
            return
        
        for archivist in self._archivists:
            archivist.record_user_command(command)
        if not command.endswith('\n'):
            command += '\n'
        try:
            self._comm_port.send_command(command)
        except Exception as e:
            for archivist in self._archivists:
                archivist.record_system_error(str(e))
            raise
    
    def _process_response(self, response: str) -> None:
        for archivist in self._archivists:
            archivist.record_system_response(response)
