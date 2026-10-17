import argparse
import asyncio
import logging

from syslogger import listener, web
from syslogger.db import Database


async def run(args):
    db = Database(args.db)
    db.purge(args.keep_days)
    await listener.start(db, args.host, args.port)
    await web.start(db, args.host, args.web_port)
    while True:
        await asyncio.sleep(3600)
        db.purge(args.keep_days)


def main():
    p = argparse.ArgumentParser(description="Simple syslog receiver with web UI")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=5514, help="syslog UDP+TCP port (default 5514)")
    p.add_argument("--web-port", type=int, default=8080)
    p.add_argument("--db", default="syslog.db")
    p.add_argument("--keep-days", type=int, default=30)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
