# SysLogger

A small syslog server with a live web page. It receives syslog over UDP and TCP
(RFC 3164 and RFC 5424, plus Tasmota's format), stores messages in SQLite, and shows them
in your browser with search, severity and host filters.

## Usage

1. Install and start the add-on.
2. Open the web UI at `http://<your-home-assistant-ip>:8515`.
3. Point your devices at `<your-home-assistant-ip>`, port `5514` (UDP or TCP).

For Tasmota, run these in the device console:

```
LogHost <your-home-assistant-ip>
LogPort 5514
SysLog 3
```

The cards at the top show when each host last sent a message. They turn amber after
1 minute and red after 3 minutes of silence, which makes a stalled device easy to spot.

## Options

| Option | Default | Meaning |
|---|---|---|
| `keep_days` | 30 | Messages older than this many days are deleted. |

## Ports

| Port | Use |
|---|---|
| 5514/udp, 5514/tcp | Syslog. You can change the host port under the add-on's Network settings; devices that only support the standard port 514 can use host port 514 mapped to 5514. |
| 8515/tcp | Web UI. |

## Security

The web UI has no login. Anyone who can reach port 8515 can read your logs, so keep it on a
trusted network and do not expose it to the internet.

## Data

The database is stored in the add-on's `/data` folder and survives restarts and updates.
It is removed if you uninstall the add-on.
