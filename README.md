# SysLogger

Small syslog receiver (UDP + TCP, RFC 3164 and 5424) with a live web UI. Python standard library only.

## Run
```
python main.py                 # syslog on :5514, web UI on http://localhost:8080
python main.py --port 514      # needs an admin terminal on Windows
python tools/send_test.py      # send sample messages (add --tcp for TCP)
python -m unittest discover tests
```

Options: `--host`, `--port`, `--web-port`, `--db`, `--keep-days` (default 30).

Point devices at `<this PC's IP>:5514`. Allow inbound UDP/TCP 5514 in Windows Firewall.
In VS Code, use the "SysLogger" launch configuration (F5).

## Home Assistant add-on
This folder is also a local add-on (`config.yaml`, `Dockerfile`, `run.sh`).
1. Copy the whole folder to `/addons/syslogger` on the HA host (Samba "addons" share, or the SSH add-on).
2. Settings > Add-ons > Add-on Store > menu (top right) > Check for updates.
3. Under "Local add-ons" open SysLogger > Install > enable "Start on boot" > Start.
4. Web UI: `http://<ha-ip>:8515`. Syslog: `<ha-ip>:5514` (UDP and TCP). The database is kept in the add-on's `/data`.

On a Tasmota device: `LogHost <ha-ip>`, `LogPort 5514`, `SysLog 3`.

The web UI has no authentication; keep it on a trusted network.
