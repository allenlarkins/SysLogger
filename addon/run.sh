#!/bin/sh
# Home Assistant add-on entry point. Options live in /data/options.json; the database in /data persists.
KEEP_DAYS=$(python -c "import json; print(json.load(open('/data/options.json')).get('keep_days', 30))")
exec python -u main.py --db /data/syslog.db --port 5514 --web-port 8515 --keep-days "$KEEP_DAYS"
