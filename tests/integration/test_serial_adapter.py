import pytest
import time
import os
from serial import SerialException

from fonny.adapters.serial_adapter import SerialAdapter
from fonny.ports.character_handler_port import CharacterHandlerPort


class MockCharacterHandler(CharacterHandlerPort):
    """Mock implementation of CharacterHandlerPort for integration testing."""
    
    def __init__(self):
        """Initialize the mock character handler."""
        self.received_chars = []
    
    def handle_character(self, char: str) -> None:
        """Handle a character by storing it."""
        self.received_chars.append(char)
    
    def get_received_text(self) -> str:
        """Get all received characters as a string."""
        return ''.join(self.received_chars)
    
    def clear(self) -> None:
        """Clear all received characters."""
        self.received_chars = []


# Skip these tests if the Pico is not connected
skip_if_no_pico = pytest.mark.skipif(
    not os.path.exists('/dev/ttyACM0'),
    reason="Pico device not connected at /dev/ttyACM0"
)


@skip_if_no_pico
class TestSerialAdapter:
    """Integration tests for the SerialAdapter class with a real Pico device."""
    
    @pytest.fixture
    def serial_adapter(self):
        """Create a SerialAdapter connected to a real Pico device."""
        # Create a character handler to receive responses
        handler = MockCharacterHandler()
        
        # Create and connect the adapter
        adapter = SerialAdapter(
            character_handler=handler,
            port='/dev/ttyACM0',
            baud_rate=115200,
            timeout=1
        )
        
        # Connect to the Pico
        connected = adapter.connect()
        if not connected:
            pytest.skip("Failed to connect to Pico device")
        
        # Clear any pending output
        adapter.clear_buffer()
        
        # Wait for the connection to stabilize
        time.sleep(0.5)
        
        # Return the adapter and handler for use in tests
        yield (adapter, handler)
        
        # Disconnect after the test
        adapter.disconnect()
    
    def test_send_forth_command_and_receive_response(self, serial_adapter):
        """Test sending a Forth command and receiving the response."""
        adapter, handler = serial_adapter
        
        # Clear any previous characters
        handler.clear()
        
        # Send a simple Forth command that adds two numbers
        command = "2 2 + ."
        adapter.send_command(command + "\r\n")
        
        # Wait for the response
        time.sleep(1)
        
        # Get the response from the character handler
        response = handler.get_received_text()
        
        # Verify the response contains the command and the result
        assert command in response
        assert "4  ok" in response
