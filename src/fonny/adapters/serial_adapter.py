import time
from typing import Optional

import serial
from serial import SerialException

from fonny.ports.communication_port import CommunicationPort


class SerialAdapter(CommunicationPort):
    """
    Adapter for serial communication with a FORTH system.
    Implements the CommunicationPort interface.
    """
    
    def __init__(self, port: str = '/dev/ttyACM0', baud_rate: int = 115200, timeout: int = 1):
        """
        Initialize the serial adapter.
        
        Args:
            port: Serial port path
            baud_rate: Baud rate for serial communication
            timeout: Timeout in seconds for serial operations
        """
        self._port = port
        self._baud_rate = baud_rate
        self._timeout = timeout
        self._serial: Optional[serial.Serial] = None
    
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
            return True
        except SerialException as e:
            print(f"Error opening serial port: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from the FORTH system.
        """
        if self._serial and self._serial.is_open:
            self._serial.close()
            self._serial = None
    
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
