import pytest
import time
import threading
from queue import Queue

from fonny.adapters.serial_adapter import SerialAdapter
from fonny.ports.character_handler_port import CharacterHandlerPort


class TestCharacterHandler(CharacterHandlerPort):
    """
    Test implementation of CharacterHandlerPort that collects characters
    for verification in tests.
    """
    
    def __init__(self):
        self.received_chars = []
        self.response_complete = False
        
    def handle_character(self, char: str) -> None:
        """
        Handle a single character by adding it to the received_chars list.
        
        Args:
            char: The character received
        """
        print(f"Received character: {repr(char)}")  # Debug output
        self.received_chars.append(char)
        
        # Check if the response is complete (contains "ok")
        received_text = ''.join(self.received_chars)
        if "ok" in received_text:
            self.response_complete = True
            print("Response complete: 'ok' found in output")
            
    def get_received_text(self) -> str:
        """
        Get the complete text received so far.
        
        Returns:
            str: The concatenated received characters
        """
        return ''.join(self.received_chars)


class TestSerialAdapterIntegration:
    """Integration tests for the SerialAdapter class."""
    
    def test_character_by_character_reading(self):
        """
        Test that the SerialAdapter can read data character by character in real-time.
        
        This test connects to a real Pico and verifies that characters are received
        as they arrive, without waiting for a complete response.
        """
        # Create a character handler to process received characters
        char_handler = TestCharacterHandler()
        
        # Create the adapter with the character handler
        print("Creating SerialAdapter with character handler")
        adapter = SerialAdapter(character_handler=char_handler)
        
        # Connect to the Pico
        print(f"Connecting to Pico on port {adapter._port}")
        connected = adapter.connect()
        if not connected:
            pytest.skip("Could not connect to the Pico. Test skipped.")
        
        print(f"Successfully connected to Pico")
        
        try:
            # Send a command that should produce a multi-line response
            test_command = "words\n"
            print(f"Sending command: {repr(test_command)}")
            adapter.send_command(test_command)
            
            # Wait for the response with a timeout
            max_wait_time = 5  # Maximum wait time in seconds
            wait_interval = 0.1  # Check interval in seconds
            elapsed_time = 0
            
            print("Waiting for response...")
            while elapsed_time < max_wait_time and not char_handler.response_complete:
                time.sleep(wait_interval)
                elapsed_time += wait_interval
                
                # Print progress updates
                if elapsed_time % 1 < wait_interval:  # Every second
                    print(f"Waiting for response... {elapsed_time:.1f}s elapsed")
                    print(f"Characters received so far: {len(char_handler.received_chars)}")
                    if char_handler.received_chars:
                        print(f"Last character: {repr(char_handler.received_chars[-1])}")
                        print(f"Current text: {repr(char_handler.get_received_text())}")
            
            # Print the final result
            print(f"Response complete after {elapsed_time:.1f} seconds")
            print(f"Received text: {repr(char_handler.get_received_text())}")
            
            # Verify that we received a response
            assert len(char_handler.received_chars) > 0, "No characters received from the Pico"
            
            # Verify that the response contains the expected elements
            received_text = char_handler.get_received_text()
            print(f"Final received text: {repr(received_text)}")
            assert "words" in received_text, "Response should contain the command echo"
            assert "ok" in received_text, "Response should contain 'ok'"
            
            # Verify that we received multiple words (FORTH words listing)
            # We expect at least 10 words in any FORTH system
            word_count = len(received_text.split())
            assert word_count > 10, "Expected at least 10 words in the output"
            
            # Verify that the response contains at least one newline (multi-line response)
            assert "\n" in received_text, "Response should be multi-line"
            
        finally:
            # Clean up
            print("Disconnecting from Pico")
            adapter.disconnect()
