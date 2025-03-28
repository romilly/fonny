import pytest

from hamcrest import assert_that

from fonny.adapters.serial_adapter import SerialAdapter
from fonny.ports.character_handler_port import CharacterHandlerPort
from helpers.waiter import wait_until


class MockCharacterHandler(CharacterHandlerPort):
    """
    Test implementation of CharacterHandlerPort that collects characters
    for verification in tests.
    """

    def __init__(self):
        self.received_chars = []
        self.response_complete = False

    def handle_character(self, char_received: str) -> None:
        self.received_chars.append(char_received)

        # Check if the response is complete (contains "ok")
        received_text = ''.join(self.received_chars)
        if "ok" in received_text:
            self.response_complete = True

    def get_received_text(self) -> str:
        return ''.join(self.received_chars)


class TestSerialAdapterIntegration:
    """Integration tests for the SerialAdapter class."""
    
    def test_character_by_character_reading(self):
        char_handler = MockCharacterHandler()
        adapter = SerialAdapter(character_handler=char_handler)
        connected = adapter.connect()
        if not connected:
            pytest.skip("Could not connect to the Pico. Test skipped.")
        try:
            adapter.clear_buffer()
            test_command = "words\n"
            adapter.send_command(test_command)
            
            def find_ok():
                received_text = char_handler.get_received_text()
                return 'ok' in received_text

            assert_that(wait_until(find_ok), 'response should end with ok')
        finally:
            # Clean up
            adapter.clear_buffer()
