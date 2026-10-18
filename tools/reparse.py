"""Re-run the current parser over stored rows whose host is still just the sender's IP.

Usage: python tools/reparse.py [--db syslog.db]
Stop SysLogger first if you can; a copy of the DB is made as <db>.bak before any change.
"""
import argparse
import os
import shutil
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from syslogger.parser import parse


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="syslog.db")
    args = p.parse_args()

    shutil.copyfile(args.db, args.db + ".bak")
    conn = sqlite3.connect(args.db, timeout=10)
    rows = conn.execute("SELECT id, source_ip, raw FROM messages WHERE host = source_ip").fetchall()
    updated = 0
    for id_, ip, raw in rows:
        r = parse(raw, ip)
        if r["host"] != ip:
            conn.execute("UPDATE messages SET host=?, app=?, message=? WHERE id=?",
                         (r["host"], r["app"], r["message"], id_))
            updated += 1
    conn.commit()
    print(f"checked {len(rows)} rows, updated {updated}. Backup: {args.db}.bak")


if __name__ == "__main__":
    main()
