# SysLogger

A small syslog receiver (UDP + TCP, RFC 3164 and 5424, plus Tasmota's format) with a live web UI.
Python standard library only. It runs as a **Home Assistant add-on** or as a plain Python script.

## Home Assistant add-on

[![Add this repository to your Home Assistant instance.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fallenlarkins%2FSysLogger)

1. Click the button above, or in Home Assistant go to **Settings > Add-ons > Add-on Store >
   menu (top right) > Repositories** and add `https://github.com/allenlarkins/SysLogger`.
2. Find **SysLogger** in the store, click **Install**, enable **Start on boot**, then **Start**.
3. Open `http://<ha-ip>:8515`. Point your devices at `<ha-ip>`, port `5514` (UDP or TCP).

For Tasmota, in the device console: `LogHost <ha-ip>`, `LogPort 5514`, `SysLog 3`.

More detail is in [addon/DOCS.md](addon/DOCS.md). The database lives in the add-on's `/data` and
survives updates.

## Run it on your own machine

```
python addon/main.py                  # syslog on :5514, web UI on http://localhost:8080
python addon/main.py --port 514       # needs an admin / root terminal
python tools/send_test.py             # send sample messages (add --tcp for TCP)
python -m unittest discover tests
```

Options: `--host`, `--port`, `--web-port`, `--db`, `--keep-days` (default 30).
In VS Code, use the "SysLogger" launch configuration (F5).

`python tools/reparse.py --db syslog.db` re-runs the parser over stored rows (after a parser
improvement), keeping a `.bak` copy first.

## Layout

```
repository.yaml     marks this repo as a Home Assistant add-on repository
addon/              the add-on: config.yaml, Dockerfile, run.sh, DOCS.md, and the app itself
tests/, tools/      unit tests and helper scripts
```

## Security

The web UI has no authentication. Keep it on a trusted network and do not expose it to the internet.
