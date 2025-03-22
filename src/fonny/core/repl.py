from typing import Optional, List, Callable
from fonny.ports.communication_port import CommunicationPort


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
        self._response_handlers: List[Callable[[str], None]] = []
    
    def start(self) -> bool:
        """
        Start the REPL by connecting to the FORTH system.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        return self._comm_port.connect()
    
    def stop(self) -> None:
        """
        Stop the REPL by disconnecting from the FORTH system.
        """
        if self._comm_port.is_connected():
            self._comm_port.disconnect()
    
    def process_command(self, command: str) -> None:
        """
        Process a command by sending it to the FORTH system.
        
        Args:
            command: The command to send
        """
        if command.lower() == 'exit':
            return
            
        if not command.endswith('\n'):
            command += '\n'
        
        self._comm_port.send_command(command)
        
        # Process responses
        self._process_responses()
    
    def _process_responses(self) -> None:
        """
        Process responses from the FORTH system.
        """
        while True:
            response = self._comm_port.receive_response()
            if not response:
                break
                
            # Notify all response handlers
            for handler in self._response_handlers:
                handler(response)
    
    def add_response_handler(self, handler: Callable[[str], None]) -> None:
        """
        Add a handler function that will be called with each response.
        
        Args:
            handler: A function that takes a response string as input
        """
        self._response_handlers.append(handler)
    
    def remove_response_handler(self, handler: Callable[[str], None]) -> None:
        """
        Remove a previously added response handler.
        
        Args:
            handler: The handler to remove
        """
        if handler in self._response_handlers:
            self._response_handlers.remove(handler)
    
    def run_interactive_session(self) -> None:
        """
        Run an interactive session where the user can type commands and see responses.
        """
        if not self._comm_port.is_connected():
            if not self.start():
                print("Failed to connect to the FORTH system")
                return
        
        print("Interactive FORTH session started. Type 'exit' to quit.")
        
        # Add console output handler
        def console_handler(response: str) -> None:
            print(f"Received: {response}")
        
        self.add_response_handler(console_handler)
        
        try:
            while True:
                # Get user input
                user_input = input("> ")
                
                # Check if user wants to exit
                if user_input.lower() == 'exit':
                    break
                
                # Process the command
                self.process_command(user_input)
                
        except KeyboardInterrupt:
            print("\nSession terminated by user")
        except Exception as e:
            print(f"Error during session: {e}")
        finally:
            self.remove_response_handler(console_handler)
            self.stop()
