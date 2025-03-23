import pytest
import time
import threading
from queue import Queue

from fonny.adapters.serial_adapter import SerialAdapter


class TestSerialAdapterIntegration:
    """Integration tests for the SerialAdapter class."""
    
    def test_character_by_character_reading(self):
        """
        Test that the SerialAdapter can read data character by character in real-time.
        
        This test connects to a real Pico and verifies that characters are received
        as they arrive, without waiting for a complete response.
        """
        # Create a queue to store received characters
        char_queue = Queue()
        
        # Create the adapter
        adapter = SerialAdapter()
        
        # Connect to the Pico
        connected = adapter.connect()
        if not connected:
            pytest.skip("Could not connect to the Pico. Test skipped.")
        
        try:
            # Set up a thread to read characters from the serial port
            stop_thread = threading.Event()
            
            def read_chars():
                while not stop_thread.is_set():
                    if adapter._serial.in_waiting > 0:
                        char = adapter._serial.read(1).decode('utf-8', errors='replace')
                        char_queue.put(char)
                    else:
                        # Short sleep to prevent high CPU usage
                        time.sleep(0.01)
            
            # Start the reading thread
            read_thread = threading.Thread(target=read_chars)
            read_thread.daemon = True
            read_thread.start()
            
            # Send a command that should produce a multi-line response
            test_command = "words\n"
            adapter.send_command(test_command)
            
            # Wait for the response with a timeout
            max_wait_time = 5  # Maximum wait time in seconds
            wait_interval = 0.1  # Check interval in seconds
            elapsed_time = 0
            response_complete = False
            received_chars = []
            
            while elapsed_time < max_wait_time and not response_complete:
                time.sleep(wait_interval)
                elapsed_time += wait_interval
                
                # Get all available characters from the queue
                while not char_queue.empty():
                    received_chars.append(char_queue.get())
                
                # Check if "ok" appears in the received text, indicating the response is complete
                received_text = ''.join(received_chars)
                if "ok" in received_text:
                    response_complete = True
                    print(f"Response complete after {elapsed_time:.1f} seconds")
                    print(f"Received text: {repr(received_text)}")
            
            # Stop the reading thread
            stop_thread.set()
            read_thread.join(timeout=1.0)
            
            # Verify that we received a response
            assert len(received_chars) > 0, "No characters received from the Pico"
            
            # Verify that the response contains the expected elements
            received_text = ''.join(received_chars)
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
            adapter.disconnect()
