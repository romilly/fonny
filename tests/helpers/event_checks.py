import json
import sqlite3


def get_events_from_db(test_db_path, event_type=None) -> dict:
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()

    if event_type:
        cursor.execute(
            "SELECT id, event_type, timestamp, data FROM events WHERE event_type = ? ORDER BY id",
            (event_type.name,)
        )
    else:
        cursor.execute("SELECT id, event_type, timestamp, data FROM events ORDER BY id")

    rows = cursor.fetchall()
    conn.close()
    events = []
    for row in rows:
        event = dict(row)
        event['data'] = json.loads(event['data'])
        events.append(event)

    return events
