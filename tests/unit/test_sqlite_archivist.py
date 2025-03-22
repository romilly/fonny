import os
import sqlite3
import json
from datetime import datetime

import pytest

from fonny.adapters.sqlite_archivist import SQLiteArchivist
from fonny.ports.archivist_port import EventType


class TestSQLiteArchivist:
    """Tests for the SQLiteArchivist class."""
    
    @pytest.fixture
    def db_path(self):
        """Fixture to provide a temporary database path."""
        path = "test_events.db"
        yield path
        # Clean up after test
        if os.path.exists(path):
            os.remove(path)
    
    def test_initialization_creates_db(self, db_path):
        """Test that initializing the archivist creates the database."""
        # Act
        SQLiteArchivist(db_path)
        
        # Assert
        assert os.path.exists(db_path)
        
        # Verify schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_record_user_command(self, db_path):
        """Test that record_user_command stores the command in the database."""
        # Arrange
        archivist = SQLiteArchivist(db_path)
        
        # Act
        archivist.record_user_command("test command")
        
        # Assert
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT event_type, data FROM events")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 1
        event_type, data_json = rows[0]
        assert event_type == EventType.USER_COMMAND.name
        data = json.loads(data_json)
        assert data["command"] == "test command"
    
    def test_record_system_response(self, db_path):
        """Test that record_system_response stores the response in the database."""
        # Arrange
        archivist = SQLiteArchivist(db_path)
        
        # Act
        archivist.record_system_response("test response")
        
        # Assert
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT event_type, data FROM events")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 1
        event_type, data_json = rows[0]
        assert event_type == EventType.SYSTEM_RESPONSE.name
        data = json.loads(data_json)
        assert data["response"] == "test response"
    
    def test_record_system_error(self, db_path):
        """Test that record_system_error stores the error in the database."""
        # Arrange
        archivist = SQLiteArchivist(db_path)
        
        # Act
        archivist.record_system_error("test error")
        
        # Assert
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT event_type, data FROM events")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 1
        event_type, data_json = rows[0]
        assert event_type == EventType.SYSTEM_ERROR.name
        data = json.loads(data_json)
        assert data["error"] == "test error"
    
    def test_record_connection_events(self, db_path):
        """Test that record_connection_opened and record_connection_closed store events in the database."""
        # Arrange
        archivist = SQLiteArchivist(db_path)
        
        # Act
        archivist.record_connection_opened()
        archivist.record_connection_closed()
        
        # Assert
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT event_type FROM events ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 2
        assert rows[0][0] == EventType.CONNECTION_OPENED.name
        assert rows[1][0] == EventType.CONNECTION_CLOSED.name
    
    def test_timestamp_is_stored(self, db_path):
        """Test that the timestamp is stored in the database."""
        # Arrange
        archivist = SQLiteArchivist(db_path)
        
        # Act
        archivist.record_user_command("test command")
        
        # Assert
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp FROM events")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 1
        timestamp_str = rows[0][0]
        # Verify that the timestamp is in ISO format
        try:
            datetime.fromisoformat(timestamp_str)
            valid_timestamp = True
        except ValueError:
            valid_timestamp = False
        
        assert valid_timestamp
