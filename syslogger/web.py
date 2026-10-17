import asyncio
import json
import logging
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .parser import SEVERITIES

log = logging.getLogger("syslogger.web")
STATIC = Path(__file__).resolve().parent.parent / "static"


def _response(status, body, ctype):
    reason = {200: "OK", 404: "Not Found", 405: "Method Not Allowed"}[status]
    head = (f"HTTP/1.1 {status} {reason}\r\nContent-Type: {ctype}\r\n"
            f"Content-Length: {len(body)}\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n")
    return head.encode() + body


def _int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def make_handler(db):
    async def handle(reader, writer):
        try:
            request_line = await reader.readline()
            while (await reader.readline()).strip():  # drain headers
                pass
            parts = request_line.decode("latin-1").split()
            if len(parts) < 2 or parts[0] != "GET":
                writer.write(_response(405, b"Method Not Allowed", "text/plain"))
            else:
                url = urlparse(parts[1])
                qs = {k: v[0] for k, v in parse_qs(url.query).items()}
                if url.path == "/api/messages":
                    rows = db.query(
                        since_id=_int(qs.get("since_id"), 0),
                        severity=_int(qs.get("severity")),
                        host=qs.get("host"),
                        q=qs.get("q"),
                        limit=min(_int(qs.get("limit"), 500), 2000),
                    )
                    body = json.dumps({"messages": rows, "hosts": db.hosts(), "severities": SEVERITIES})
                    writer.write(_response(200, body.encode(), "application/json"))
                elif url.path == "/api/hosts":
                    writer.write(_response(200, json.dumps(db.last_seen()).encode(), "application/json"))
                elif url.path in ("/", "/index.html"):
                    writer.write(_response(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8"))
                else:
                    writer.write(_response(404, b"Not Found", "text/plain"))
            await writer.drain()
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        finally:
            writer.close()

    return handle


async def start(db, host, port):
    server = await asyncio.start_server(make_handler(db), host, port)
    log.info("Web UI at http://localhost:%d", port)
    return server
