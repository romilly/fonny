from typing import Optional, List
from fonny.ports.communication_port import CommunicationPort
from fonny.ports.archivist_port import ArchivistPort


class ForthRepl:
    """
    Core REPL (Read-Eval-Print Loop) for interacting with a FORTH system.
    This class uses a CommunicationPort to send commands and receive responses.
    """
    
    def __init__(self, communication_port: CommunicationPort):
        """
        Initialize the REPL with a communication port.
        
        Args:
            communication_port: The port to use for communication with the FORTH system
        """
        self._comm_port = communication_port
        self._archivists: List[ArchivistPort] = []
    
    def start(self) -> bool:
        """
        Start the REPL by connecting to the FORTH system.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        success = self._comm_port.connect()
        if success:
            for archivist in self._archivists:
                archivist.record_connection_opened()
        return success
    
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
            
            # Process responses
            self._process_responses()
        except Exception as e:
            # Record the error in all archivists
            for archivist in self._archivists:
                archivist.record_system_error(str(e))
            raise
    
    def _process_responses(self) -> None:
        """
        Process responses from the FORTH system.
        """
        while True:
            try:
                response = self._comm_port.receive_response()
                if not response:
                    break
                    
                # Record the response in all archivists
                for archivist in self._archivists:
                    archivist.record_system_response(response)
            except Exception as e:
                # Record the error in all archivists
                for archivist in self._archivists:
                    archivist.record_system_error(str(e))
                raise
    
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
