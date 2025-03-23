import time
import threading
from typing import Optional

import serial
from serial import SerialException

from fonny.ports.communication_port import CommunicationPort
from fonny.ports.character_handler_port import CharacterHandlerPort


class SerialAdapter(CommunicationPort):
    """
    Adapter for serial communication with a FORTH system.
    Implements the CommunicationPort interface.
    """
    
    def __init__(self, port: str = '/dev/ttyACM0', baud_rate: int = 115200, timeout: int = 1, 
                 character_handler: Optional[CharacterHandlerPort] = None):
        """
        Initialize the serial adapter.
        
        Args:
            port: Serial port path
            baud_rate: Baud rate for serial communication
            timeout: Timeout in seconds for serial operations
            character_handler: Handler for processing characters as they arrive
        """
        self._port = port
        self._baud_rate = baud_rate
        self._timeout = timeout
        self._serial: Optional[serial.Serial] = None
        self._character_handler = character_handler
        self._stop_reading = threading.Event()
        self._read_thread = None
    
    def connect(self) -> bool:
        """
        Connect to the FORTH system via serial port.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baud_rate,
                timeout=self._timeout
            )
            
            # Start the reading thread if we have a character handler
            if self._character_handler:
                self._start_reading_thread()
                
            return True
        except SerialException as e:
            print(f"Error opening serial port: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from the FORTH system.
        """
        # Stop the reading thread if it's running
        if self._read_thread and self._read_thread.is_alive():
            self._stop_reading.set()
            self._read_thread.join(timeout=1.0)
        
        if self._serial and self._serial.is_open:
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
        Read characters from the serial port and pass them to the character handler.
        This method runs in a background thread.
        """
        while not self._stop_reading.is_set() and self.is_connected():
            if self._serial.in_waiting > 0:
                char = self._serial.read(1).decode('utf-8', errors='replace')
                if self._character_handler:
                    self._character_handler.handle_character(char)
            else:
                # Short sleep to prevent high CPU usage
                time.sleep(0.01)
    
    def send_command(self, command: str) -> None:
        """
        Send a command to the FORTH system.
        
        Args:
            command: The command to send
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FORTH system")
        
        self._serial.write(command.encode())
    
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
        
        # Wait a bit for the device to respond
        time.sleep(0.2)
        
        if self._serial.in_waiting:
            response = self._serial.readline().decode('utf-8', errors='replace').strip()
            return response
        
        return None
    
    def is_connected(self) -> bool:
        """
        Check if the connection to the FORTH system is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._serial is not None and self._serial.is_open
