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
from time import sleep

import pytest
from hamcrest import assert_that

from fonny.adapters.rqlite_archivist import RQLiteArchivist
from fonny.gui.forth_gui import ForthGui
from fonny.core.repl import ForthRepl
from fonny.adapters.serial_adapter import SerialAdapter
from fonny.ports.archivist_port import EventType
from helpers.waiter import wait_until
from tests.helpers.tk_testing import push, type_in


class TestForthGui(unittest.TestCase):
    """End-to-end test for the Fonny GUI with an actual Pico connection."""
    
    @classmethod
    def setUpClass(cls):
        # Create a test database path

        cls.archivist = RQLiteArchivist(port=4003)
        cls.repl = ForthRepl(cls.archivist)
        cls.serial_adapter = SerialAdapter(character_handler=cls.repl)
        cls.repl.set_communication_port(cls.serial_adapter)
        cls.gui = ForthGui(cls.repl, title="Fonny Test")
        cls.gui.update()

    @classmethod
    def tearDownClass(cls):
        cls.repl.stop()
        cls.gui.cleanup()


    def setUp(self):
        self.archivist.clear_tables()
        self.gui.clear_output()
        self.gui.update()

    def tearDown(self):
        pass


    def test_connect_and_send_command(self):
        push(self.gui._connect_button)
        self.gui.update()
        self.assertTrue(self.repl._comm_port.is_connected(), "Failed to connect to Pico")
        connection_events = self.archivist.get_events(EventType.CONNECTION_OPENED)
        self.assertGreaterEqual(len(connection_events), 1, "Connection opened event not recorded")
        test_command = "2 2 + ."
        type_in(self.gui._command_input, test_command)
        push(self.gui._send_button)

        def check_output_value(text: str):
            self.gui.update()
            value = self.gui._output.value
            return text in value

        self.assertTrue(wait_until(check_output_value, ['4']), f"4 not in gui output")
        self.assertIn("ok", self.gui._output.value, "Expected 'ok' in response")
        command_events = self.archivist.get_events(EventType.USER_COMMAND)
        self.assertGreaterEqual(len(command_events), 1, "User command event not recorded")
        latest_command = command_events[-1]
        expected_command = test_command + "\n"
        self.assertEqual(latest_command['data']['command'], expected_command,
                         f"Expected command '{expected_command}' but got '{latest_command['data']['command']}'")
        response_events = self.archivist.get_events(EventType.SYSTEM_RESPONSE)
        self.assertGreaterEqual(len(response_events), 1, "System response event not recorded")

    def test_error_handling(self):
        """Test that errors are properly displayed."""
        # Connect if not already connected
        if not self.repl._comm_port.is_connected():
            push(self.gui._connect_button)

        self.serial_adapter.clear_buffer()
        self.gui.clear_output()
        # Send an invalid command
        invalid_command = "invalid_command"
        type_in(self.gui._command_input, invalid_command)
        push(self.gui._send_button)
        # Verify that an error message is displayed
        def find_unable_to_parse():
            self.gui.update()
            output_text = self.gui._output.value
            return "unable to parse" in output_text

        assert_that(wait_until(find_unable_to_parse),
                    "unable to find 'unable to parse' in output")
        command_events = self.archivist.get_events(EventType.USER_COMMAND)
        self.assertGreaterEqual(len(command_events), 1, "User command event not recorded")
        invalid_command_events = [event for event in command_events
                                 if event['data']['command'] == invalid_command + "\n"]
        self.assertGreaterEqual(len(invalid_command_events), 1,
                               f"Invalid command '{invalid_command}' not found in recorded events")
        response_events = self.archivist.get_events(EventType.SYSTEM_RESPONSE)
        self.assertGreaterEqual(len(response_events), 1, "System response event not recorded")
        error_responses = [event for event in response_events
                          if "unable to parse" in event['data']['response']]
        self.assertGreaterEqual(len(error_responses), 1, "Error response not found in recorded events")
