import os

import json
from datetime import datetime
import pytest
from hamcrest import assert_that, equal_to

from fonny.adapters.rqlite_archivist import RQLiteArchivist
from fonny.ports.archivist_port import EventType

@pytest.fixture
def archivist():
    archivist = RQLiteArchivist(port=4001)
    archivist.clear_tables()
    yield archivist
    archivist.close()


class TestRQLiteArchivist:
    """Tests for the SQLiteArchivist class."""
    
    def test_record_user_command(self, archivist):
        """Test that record_user_command stores the command in the database."""
        archivist.record_user_command("test command")
        events = archivist.get_events()
        assert_that(len(events), equal_to(1))
        event = events[0]['data']
        assert_that(event["command"], equal_to("test command"))


    def test_record_system_response(self, archivist):
        """Test that record_system_response stores the response in the database."""
        archivist.record_system_response("system response")
        events = archivist.get_events()
        assert_that(len(events), equal_to(1))
        event = events[0]
        assert_that(event['event_type'], equal_to(EventType.SYSTEM_RESPONSE.name))
        assert_that(event['data']["response"], equal_to("system response"))

    def test_record_system_error(self, archivist):
        """Test that record_system_error stores the error in the database."""
        archivist.record_system_error("ouch!")
        events = archivist.get_events()
        assert_that(len(events), equal_to(1))
        event = events[0]
        assert_that(event['event_type'], equal_to(EventType.SYSTEM_ERROR.name))
        assert_that(event['data']["error"], equal_to("ouch!"))

    def test_record_connection_events(self, archivist):
        """Test that record_connection_opened and record_connection_closed store events in the database."""
        archivist.record_connection_opened()
        archivist.record_connection_closed()
        events = archivist.get_events()
        assert_that(len(events), equal_to(2))
        assert_that(events[0]['event_type'], equal_to(EventType.CONNECTION_OPENED.name))
        assert_that(events[1]['event_type'], equal_to(EventType.CONNECTION_CLOSED.name))

    # def test_timestamp_is_stored(self, db_path):
    #     """Test that the timestamp is stored in the database."""
    #     # Arrange
    #     archivist = SQLiteArchivist(db_path)
    #
    #     # Act
    #     archivist.record_user_command("test command")
    #
    #     # Assert
    #     conn = sqlite3.connect(db_path)
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT timestamp FROM events")
    #     rows = cursor.fetchall()
    #     conn.close()
    #
    #     assert len(rows) == 1
    #     timestamp_str = rows[0][0]
    #     # Verify that the timestamp is in ISO format
    #     try:
    #         datetime.fromisoformat(timestamp_str)
    #         valid_timestamp = True
    #     except ValueError:
    #         valid_timestamp = False
    #
    #     assert valid_timestamp
