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
import os
import time
import unittest
import sqlite3
import json
import pytest

from fonny.gui.forth_gui import ForthGui
from fonny.core.repl import ForthRepl
from fonny.adapters.serial_adapter import SerialAdapter
from fonny.adapters.sqlite_archivist import SQLiteArchivist
from fonny.ports.archivist_port import EventType
from tests.helpers.event_checks import get_events_from_db
from tests.helpers.tk_testing import push, type_in


class TestForthGui(unittest.TestCase):
    """End-to-end test for the Fonny GUI with an actual Pico connection."""
    
    @classmethod
    def setUpClass(cls):
        # Create a test database path
        cls.test_db_path = "test_e2e_events.db"
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        cls.archivist = SQLiteArchivist(cls.test_db_path)
        cls.repl = ForthRepl(cls.archivist)
        serial_adapter = SerialAdapter(character_handler=cls.repl)
        cls.repl.set_communication_port(serial_adapter)
        cls.gui = ForthGui(cls.repl, title="Fonny Test")
        cls.gui.update()

    @classmethod
    def tearDownClass(cls):
        cls.gui.cleanup()


    def setUp(self):
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
        
        # Verify connection event was recorded in the database
        connection_events = get_events_from_db(self.test_db_path, EventType.CONNECTION_OPENED)
        self.assertGreaterEqual(len(connection_events), 1, "Connection opened event not recorded")

        # Send the traditional FORTH test command
        test_command = "2 2 + ."
        type_in(self.gui._command_input, test_command)
        push(self.gui._send_button)

        def check_for_4():
            self.gui.update()
            return '4' in self.gui._output.value

        # Verify that we got the expected response (4 ok)
        def wait_until(condition: callable, timeout = 0.5, delay = 0.1) -> bool:
            time_end = time.time() + timeout
            while time.time() < time_end:
                if condition():
                    return True
            time.sleep(delay)
            return False
        self.assertTrue(wait_until(check_for_4), f"4 not in gui output")


        self.assertIn("4", self.gui._output.value, "Expected '4' in response")
        self.assertIn("ok", self.gui._output.value, "Expected 'ok' in response")
        
        # Verify command was recorded in the database
        # command_events = self._get_events_from_db(EventType.USER_COMMAND)
        # self.assertGreaterEqual(len(command_events), 1, "User command event not recorded")
        
        # Check the most recent command event
        # latest_command = command_events[-1]
        # The command in the database will have a newline appended
        # expected_command = test_command + "\n"
        # self.assertEqual(latest_command['data']['command'], expected_command,
        #                  f"Expected command '{expected_command}' but got '{latest_command['data']['command']}'")
        #
        # Verify response was recorded in the database
        response_events = get_events_from_db(self.test_db_path, EventType.SYSTEM_RESPONSE)
        # self.assertGreaterEqual(len(response_events), 1, "System response event not recorded")

    @pytest.mark.skip(reason="Experimenting")
    def test_error_handling(self):
        """Test that errors are properly displayed."""
        # Connect if not already connected
        if not self.repl._comm_port.is_connected():
            push(self.gui._connect_button)
            time.sleep(1.0)
            self.gui.update()
        
        # Send an invalid command
        invalid_command = "invalid_command"
        type_in(self.gui._command_input, invalid_command)
        push(self.gui._send_button)
        
        # Wait for response
        time.sleep(1)
        self.gui.update()
        
        # Verify that an error message is displayed
        output_text = self.gui._output.value
        
        # The actual error message contains "unable to parse" but may include ANSI escape codes
        # We'll just check if the command and "unable to parse" are both in the output
        self.assertIn(invalid_command, output_text, f"Command '{invalid_command}' not found in output")
        self.assertIn("unable to parse", output_text, "Error message 'unable to parse' not found in output")
        
        # Verify command was recorded in the database
        command_events = self._get_events_from_db(EventType.USER_COMMAND)
        self.assertGreaterEqual(len(command_events), 1, "User command event not recorded")
        
        # Find the command event for our invalid command
        invalid_command_events = [event for event in command_events 
                                 if event['data']['command'] == invalid_command + "\n"]
        self.assertGreaterEqual(len(invalid_command_events), 1, 
                               f"Invalid command '{invalid_command}' not found in recorded events")
        
        # Verify response containing error was recorded in the database
        response_events = self._get_events_from_db(EventType.SYSTEM_RESPONSE)
        self.assertGreaterEqual(len(response_events), 1, "System response event not recorded")
        
        # At least one response should contain the error message
        error_responses = [event for event in response_events 
                          if "unable to parse" in event['data']['response']]
        self.assertGreaterEqual(len(error_responses), 1, "Error response not found in recorded events")

    @pytest.mark.skip(reason="Experimenting")
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
        
        # Check for the result in the output
        # The exact format may vary depending on the FORTH implementation
        self.assertIn("4", output_text, "Expected result '4' not found in output")
        
        # Verify command was recorded in the database
        command_events = self._get_events_from_db(EventType.USER_COMMAND)
        self.assertGreaterEqual(len(command_events), 1, "User command event not recorded")
        
        # Find the command event for our test command
        test_command_events = [event for event in command_events 
                              if event['data']['command'] == test_command + "\n"]
        self.assertGreaterEqual(len(test_command_events), 1, 
                               f"Test command '{test_command}' not found in recorded events")
        
        # Verify response was recorded in the database
        response_events = self._get_events_from_db(EventType.SYSTEM_RESPONSE)
        self.assertGreaterEqual(len(response_events), 1, "System response event not recorded")
        
        # At least one response should contain the expected output
        output_responses = [event for event in response_events 
                           if "4" in event['data']['response']]
        self.assertGreaterEqual(len(output_responses), 1, "Expected response not found in recorded events")


if __name__ == "__main__":
    unittest.main()
