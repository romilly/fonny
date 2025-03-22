import json
import sqlite3
from typing import Dict, Any
from datetime import datetime

from fonny.ports.archivist_port import ArchivistPort, EventType


class SQLiteArchivist(ArchivistPort):
    """
    SQLite implementation of the ArchivistPort interface.
    Stores events in an SQLite database.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the SQLite archivist with a database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self._db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        # Create events table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            data TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_event(self, event_type: EventType, data: Dict[str, Any], timestamp: datetime) -> None:
        """
        Record an event in the SQLite database.
        
        Args:
            event_type: The type of event
            data: Additional data associated with the event
            timestamp: Timestamp for the event
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        # Convert timestamp to ISO format string
        timestamp_str = timestamp.isoformat()
        
        # Convert data to JSON string
        data_json = json.dumps(data)
        
        # Insert the event into the database
        cursor.execute(
            'INSERT INTO events (event_type, timestamp, data) VALUES (?, ?, ?)',
            (event_type.name, timestamp_str, data_json)
        )
        
        conn.commit()
        conn.close()
