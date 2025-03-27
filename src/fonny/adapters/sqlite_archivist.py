import json
import sqlite3
from typing import Dict, Any, List
from datetime import datetime

from fonny.ports.archivist_port import ArchivistPort, EventType


class SQLiteArchivist(ArchivistPort):
    """
    SQLite implementation of the ArchivistPort interface.
    Stores events in an SQLite database.
    """
    
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection = sqlite3.connect(self._db_path)
        self._cursor = self._connection.cursor()

        # Create events table if it doesn't exist
        self._cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            data TEXT NOT NULL
        )
        ''')

        self._connection.commit()

    def record_event(self, event_type: EventType, data: Dict[str, Any], timestamp: datetime) -> None:
        timestamp_str = timestamp.isoformat()
        data_json = json.dumps(data)
        self._cursor.execute(
            'INSERT INTO events (event_type, timestamp, data) VALUES (?, ?, ?)',
            (event_type.name, timestamp_str, data_json)
        )
        self._connection.commit()

    def get_events_from_db(self, event_type=None) -> List[dict]:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row  # This enables column access by name
        cursor = connection.cursor()
        if event_type:
            cursor.execute(
                "SELECT id, event_type, timestamp, data FROM events WHERE event_type = ? ORDER BY id",
                (event_type.name,)
            )
        else:
            cursor.execute("SELECT id, event_type, timestamp, data FROM events ORDER BY id")
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        events = []
        for row in rows:
            event = dict(row)
            event['data'] = json.loads(event['data'])
            events.append(event)
        return events

