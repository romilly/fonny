import time
import threading
from typing import Optional
from queue import Queue

import serial
from serial import SerialException

from fonny.ports.communication_port import CommunicationPort
from fonny.ports.character_handler_port import CharacterHandlerPort


class SerialAdapter(CommunicationPort):
    """
    Adapter for serial communication with a FORTH system.
    Implements the CommunicationPort interface.
    """
    
    def __init__(self, character_handler: CharacterHandlerPort, port: str = '/dev/ttyACM0', 
                 baud_rate: int = 115200, timeout: int = 1):
        """
        Initialize the serial adapter.
        
        Args:
            character_handler: Handler for processing characters as they arrive
            port: Serial port path
            baud_rate: Baud rate for serial communication
            timeout: Timeout in seconds for serial operations
        """
        self._port = port
        self._baud_rate = baud_rate
        self._timeout = timeout
        self._serial: Optional[serial.Serial] = None
        self._character_handler = character_handler
        self._stop_reading = threading.Event()
        self._read_thread = None
        self._char_queue = Queue()
    
    def connect(self) -> bool:
        """
        Connect to the FORTH system via serial port.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            print(f"Attempting to connect to {self._port} at {self._baud_rate} baud")
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baud_rate,
                timeout=self._timeout
            )
            
            # Start the reading thread if we have a character handler
            self._start_reading_thread()
                
            return True
        except SerialException as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from the FORTH system.
        """
        if self.is_connected():
            # Stop the reading thread
            self._stop_reading.set()
            if self._read_thread:
                self._read_thread.join(timeout=1.0)
                self._read_thread = None
            
            # Close the serial connection
            self._serial.close()
            self._serial = None
    
    def _start_reading_thread(self) -> None:
        """
        Start a background thread to read characters from the serial port.
        """
        self._stop_reading.clear()
        self._read_thread = threading.Thread(target=self._read_characters)
        self._read_thread.daemon = True
        self._read_thread.start()
    
    def _read_characters(self) -> None:
        """
        Read characters from the serial port and put them into the queue.
        This method runs in a background thread.
        """
        while not self._stop_reading.is_set() and self.is_connected():
            try:
                if self._serial.in_waiting > 0:
                    raw_data = self._serial.read(1)
                    char = raw_data.decode('utf-8', errors='replace')
                    # Put the character in the queue instead of directly calling the handler
                    self._char_queue.put(char)
                    
                    # If there's a character handler, also pass the character directly
                    # This maintains backward compatibility with existing code
                    if self._character_handler:
                        self._character_handler.handle_character(char)
                else:
                    # Short sleep to prevent high CPU usage
                    time.sleep(0.01)
            except Exception as e:
                print(f"Error in reading thread: {e}")
                time.sleep(0.1)  # Sleep a bit longer on error
    
    def get_character_queue(self) -> Queue:
        """
        Get the queue containing characters read from the serial port.
        
        Returns:
            Queue: A thread-safe queue containing characters read from the serial port
        """
        return self._char_queue
    
    def send_command(self, command: str) -> None:
        """
        Send a command to the FORTH system.
        
        Args:
            command: The command to send
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FORTH system")
        
        print(f"Sending command: {repr(command)}")
        self._serial.write(command.encode())
        print(f"Command sent: {repr(command)}")
    
    def receive_response(self) -> Optional[str]:
        """
        Receive a response from the FORTH system.
        
        Returns:
            The response received or None if no response is available
        
        Note:
            This method is maintained for backward compatibility.
            When using a character handler, responses are processed
            character by character in real-time.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FORTH system")
        
        if self._serial.in_waiting:
            response = self._serial.readline().decode('utf-8', errors='replace')
            return response
        return None
    
    def is_connected(self) -> bool:
        """
        Check if the connection to the FORTH system is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._serial is not None and self._serial.is_open
        
    def clear_buffer(self) -> None:
        """
        Clear any data in the serial buffer.
        
        This is useful to ensure we're starting with a clean state
        before sending a new command.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FORTH system")
            
        print("Clearing serial buffer")
        while self._serial.in_waiting > 0:
            # Read and discard all available data
            discarded = self._serial.read(self._serial.in_waiting)
            time.sleep(0.1)  # Short delay to allow more data to arrive if needed
        print("Serial buffer cleared")
