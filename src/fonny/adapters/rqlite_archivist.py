import json
import pyrqlite.dbapi2 as rqlite
from typing import Dict, Any, List
from datetime import datetime

from fonny.ports.archivist_port import ArchivistPort, EventType


class RQLiteArchivist(ArchivistPort):
    """
    SQLite implementation of the ArchivistPort interface.
    Stores events in an SQLite database.
    """
    
    def __init__(self, host: str = 'localhost', port: int=4003):

        self._connection = rqlite.connect(host=host, port=port)
        # This enables column access by name
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

    def get_events(self, event_type=None) -> List[dict]:
        if event_type:
            self._cursor.execute(
                "SELECT id, event_type, timestamp, data FROM events WHERE event_type = ? ORDER BY id",
                (event_type.name,)
            )
        else:
            self._cursor.execute("SELECT id, event_type, timestamp, data FROM events ORDER BY id")
        rows = self._cursor.fetchall()
        keys = 'id,event_type,timestamp,data'.split(',')
        events = []
        for row in rows:
            event = {}
            for (index, key) in enumerate(keys):
                event[key] = row[index]
            event['data'] = json.loads(event['data'])
            events.append(event)
        return events

    def clear_tables(self) -> None:
        self._cursor.execute('DELETE FROM events')
        self._connection.commit()

    def close(self) -> None:
            self._cursor.close()
            self._connection.close()

