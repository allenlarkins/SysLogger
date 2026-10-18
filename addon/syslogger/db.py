import sqlite3
import threading
from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at TEXT NOT NULL,
    source_ip TEXT,
    facility TEXT,
    severity INTEGER,
    host TEXT,
    app TEXT,
    message TEXT,
    raw TEXT
);
CREATE INDEX IF NOT EXISTS idx_received ON messages(received_at);
CREATE INDEX IF NOT EXISTS idx_severity ON messages(severity);
CREATE INDEX IF NOT EXISTS idx_host ON messages(host);
"""


class Database:
    def __init__(self, path):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(SCHEMA)

    def insert(self, msg):
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._lock:
            self._conn.execute(
                "INSERT INTO messages (received_at, source_ip, facility, severity, host, app, message, raw)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (now, msg["source_ip"], msg["facility"], msg["severity"],
                 msg["host"], msg["app"], msg["message"], msg["raw"]),
            )
            self._conn.commit()

    def query(self, since_id=0, severity=None, host=None, q=None, limit=500):
        """Return messages with id > since_id, oldest first, at most `limit` newest of them."""
        sql = "SELECT * FROM messages WHERE id > ?"
        args = [since_id]
        if severity is not None:  # show this severity and anything more severe
            sql += " AND severity IS NOT NULL AND severity <= ?"
            args.append(severity)
        if host:
            sql += " AND host = ?"
            args.append(host)
        if q:
            sql += " AND (message LIKE ? OR app LIKE ?)"
            args += [f"%{q}%", f"%{q}%"]
        sql += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        with self._lock:
            rows = self._conn.execute(sql, args).fetchall()
        return [dict(r) for r in reversed(rows)]

    def hosts(self):
        with self._lock:
            rows = self._conn.execute(
                "SELECT DISTINCT host FROM messages WHERE host IS NOT NULL ORDER BY host"
            ).fetchall()
        return [r[0] for r in rows]

    def last_seen(self):
        """One row per host: when it last sent, its latest line, and its message count."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT m.host, m.source_ip, m.received_at, m.app, m.message, c.n"
                " FROM messages m JOIN ("
                "   SELECT MAX(id) AS mid, COUNT(*) AS n FROM messages"
                "   WHERE host IS NOT NULL GROUP BY host) c ON m.id = c.mid"
                " ORDER BY m.id DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def purge(self, keep_days):
        cutoff = (datetime.now(timezone.utc) - timedelta(days=keep_days)).isoformat(timespec="seconds")
        with self._lock:
            self._conn.execute("DELETE FROM messages WHERE received_at < ?", (cutoff,))
            self._conn.commit()
