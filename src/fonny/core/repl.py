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
    
    def __init__(self):
        """
        Initialize the REPL with a communication port.
        
        Args:
            communication_port: The port to use for communication with the FORTH system
        """
        self._comm_port = NullCommunicationAdapter()
        self._archivists: List[ArchivistPort] = []
        self._current_response = ""
        self.character_queue = Queue()
    
    def set_communication_port(self, communication_port: CommunicationPort) -> None:
        """
        Set the communication port to use for interacting with the FORTH system.
        
        Args:
            communication_port: The port to use for communication with the FORTH system
        """
        self._comm_port = communication_port
    
    def handle_character(self, char: str) -> None:
        """
        Handle a single character received from the communication port.
        
        Args:
            char: The character received
        """
        self.character_queue.put(char)
        # If we have a complete line (newline or carriage return), process it
        if char == '\n' or char == '\r':
            if self._current_response:  # Only process if we have content
                self._process_response(self._current_response)
                self._current_response = ""
        else:
            # Add the character to the current response
            self._current_response += char
    
    def start(self) -> bool:
        """
        Start the REPL by connecting to the FORTH system.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            success = self._comm_port.connect()
            if success:
                for archivist in self._archivists:
                    archivist.record_connection_opened()
            return success
        except Exception as e:
            # Record the error in all archivists
            for archivist in self._archivists:
                archivist.record_system_error(str(e))
            return False
    
    def stop(self) -> None:
        """
        Stop the REPL by disconnecting from the FORTH system.
        """
        if self._comm_port.is_connected():
            for archivist in self._archivists:
                archivist.record_connection_closed()
            self._comm_port.disconnect()
    
    def process_command(self, command: str) -> None:
        """
        Process a command by sending it to the FORTH system.
        
        Args:
            command: The command to send
        """
        if command.lower() == 'exit':
            return
        
        # Record the command in all archivists
        for archivist in self._archivists:
            archivist.record_user_command(command)
            
        if not command.endswith('\n'):
            command += '\n'
        
        try:
            self._comm_port.send_command(command)
        except Exception as e:
            # Record the error in all archivists
            for archivist in self._archivists:
                archivist.record_system_error(str(e))
            raise
    
    def _process_response(self, response: str) -> None:
        """
        Process a response from the FORTH system.
        
        Args:
            response: The response to process
        """
        # Record the response in all archivists
        for archivist in self._archivists:
            archivist.record_system_response(response)
    
    def add_archivist(self, archivist: ArchivistPort) -> None:
        """
        Add an archivist that will record events.
        
        Args:
            archivist: The archivist to add
        """
        self._archivists.append(archivist)
    
    def remove_archivist(self, archivist: ArchivistPort) -> None:
        """
        Remove a previously added archivist.
        
        Args:
            archivist: The archivist to remove
        """
        if archivist in self._archivists:
            self._archivists.remove(archivist)
    
    def clear_character_queue(self) -> None:
        """
        Clear all characters from the queue.
        This is useful when starting the application to avoid displaying
        leftover data from previous tests.
        """
        while not self.character_queue.empty():
            try:
                self.character_queue.get_nowait()
                self.character_queue.task_done()
            except Empty:
                break
    
    def run_interactive_session(self) -> None:
        """
        Run an interactive session where the user can type commands and see responses.
        """
        if not self._comm_port.is_connected():
            if not self.start():
                print("Failed to connect to the FORTH system")
                return
        
        print("Interactive FORTH session started. Type 'exit' to quit.")
        
        # Create a console output handler
        class ConsoleArchivist(ArchivistPort):
            def record_event(self, event_type, data, timestamp):
                if "response" in data:
                    print(f"Received: {data['response']}")
                elif "error" in data:
                    print(f"Error: {data['error']}")
        
        console_archivist = ConsoleArchivist()
        self.add_archivist(console_archivist)
        
        try:
            while True:
                # Get user input
                user_input = input("> ")
                
                # Check if user wants to exit
                if user_input.lower() == 'exit':
                    break
                
                # Process the command
                try:
                    self.process_command(user_input)
                except Exception as e:
                    print(f"Error during command processing: {e}")
                
        except KeyboardInterrupt:
            print("\nSession terminated by user")
        except Exception as e:
            print(f"Error during session: {e}")
        finally:
            self.remove_archivist(console_archivist)
            self.stop()
