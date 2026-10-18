import asyncio
import logging

from .parser import parse

log = logging.getLogger("syslogger.listener")
MAX_LINE = 64 * 1024


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(self, db):
        self.db = db

    def datagram_received(self, data, addr):
        self.db.insert(parse(data.decode("utf-8", "replace"), addr[0]))


async def _handle_tcp(reader, writer, db):
    ip = writer.get_extra_info("peername")[0]
    try:
        while True:
            line = await reader.readline()  # newline-framed (also covers most octet-less senders)
            if not line:
                break
            text = line.decode("utf-8", "replace")
            if text.strip():
                db.insert(parse(text, ip))
    except (ConnectionError, asyncio.LimitOverrunError):
        pass
    finally:
        writer.close()


async def start(db, host, port):
    """Start UDP and TCP listeners; returns the transport and server for shutdown."""
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(lambda: UdpProtocol(db), local_addr=(host, port))
    server = await asyncio.start_server(lambda r, w: _handle_tcp(r, w, db), host, port, limit=MAX_LINE)
    log.info("Syslog listening on %s:%d (UDP+TCP)", host, port)
    return transport, server
