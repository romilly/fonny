"""
End-to-end tests for the Fonny GUI with a real Raspberry Pi Pico.

These tests verify that the GUI can:
1. Connect to a Pico running FORTH
2. Send commands and receive responses
3. Handle errors appropriately

Requirements:
- A Raspberry Pi Pico connected to the computer
- The Pico must be running a FORTH system
- The default serial port is /dev/ttyACM0 (can be changed in the GUI)

The tests use the helper functions in tests/helpers/tk_testing.py to interact
with the guizero components.
"""
import time
import unittest

from fonny.gui.forth_gui import ForthGui
from fonny.core.repl import ForthRepl
from fonny.adapters.serial_adapter import SerialAdapter
from tests.helpers.tk_testing import push, type_in


class TestForthGui(unittest.TestCase):
    """End-to-end test for the Fonny GUI with an actual Pico connection."""
    
    @classmethod
    def setUpClass(cls):
        # Create a real ForthRepl instance
        cls.repl = ForthRepl()

        # Create a SerialAdapter with the ForthRepl as the character handler
        serial_adapter = SerialAdapter(character_handler=cls.repl)

        # Set the SerialAdapter as the communication port for the ForthRepl

        # Create the GUI with the real repl
        cls.repl.set_communication_port(serial_adapter)
        cls.gui = ForthGui(cls.repl, title="Fonny Test")
        # Allow GUI to initialize
        cls.gui.update()

    @classmethod
    def tearDownClass(cls):
        # Clean up
        cls.gui.cleanup()
        # Don't call destroy() again as it's already called in cleanup()

    def setUp(self):
        # Reset for each test
        self.gui.update()
        
    def test_connect_and_send_command(self):
        """Test connecting to the Pico and sending a simple command."""
        # Connect to the Pico
        push(self.gui._connect_button)
        # Wait for connection to establish
        time.sleep(1)
        self.gui.update()
        
        # Verify connection status
        self.assertTrue(self.repl._comm_port.is_connected(), "Failed to connect to Pico")
        
        # Send the traditional FORTH test command
        type_in(self.gui._command_input, "2 2 + .")
        push(self.gui._send_button)
        
        # Wait for response
        time.sleep(1)
        self.gui.update()
        
        # Verify that we got the expected response (4 ok)
        output_text = self.gui._output.value
        self.assertIn("4", output_text, "Expected '4' in response")
        self.assertIn("ok", output_text, "Expected 'ok' in response")
        
    def test_error_handling(self):
        """Test that errors are properly displayed."""
        # Connect if not already connected
        if not self.repl._comm_port.is_connected():
            push(self.gui._connect_button)
            time.sleep(1)
            self.gui.update()
        
        # Send an invalid command
        type_in(self.gui._command_input, "invalid_command")
        push(self.gui._send_button)
        
        # Wait for response
        time.sleep(1)
        self.gui.update()
        
        # Verify that an error message is displayed
        output_text = self.gui._output.value
        self.assertIn("unable to parse", output_text, "Error message not displayed for invalid command")

    def test_no_command_echo_in_response(self):
        """Test that commands are not displayed immediately but echoed by the FORTH system."""
        # Connect if not already connected
        if not self.repl._comm_port.is_connected():
            push(self.gui._connect_button)
            time.sleep(1)
            self.gui.update()
        
        # Clear the output first
        self.gui._output.value = ""
        self.gui.update()
        
        # Send a simple command
        test_command = "2 2 + ."
        type_in(self.gui._command_input, test_command)
        push(self.gui._send_button)
        
        # Wait for response
        time.sleep(1)
        self.gui.update()
        
        # Get the output text
        output_text = self.gui._output.value
        
        # Verify that the command is NOT shown with a ">" prefix (which would indicate manual display)
        self.assertNotIn(f"> {test_command}", output_text,
                         "Command should not be manually displayed with '>' prefix")
        
        # Check for the complete expected output format
        # The FORTH system outputs the command, result, and 'ok' all on the same line
        expected_pattern = f"{test_command} 4  ok"
        self.assertIn(expected_pattern, output_text,
                      f"Output should contain the complete pattern: '{expected_pattern}'")


if __name__ == "__main__":
    unittest.main()
