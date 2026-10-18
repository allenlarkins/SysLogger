import re

FACILITIES = [
    "kern", "user", "mail", "daemon", "auth", "syslog", "lpr", "news",
    "uucp", "cron", "authpriv", "ftp", "ntp", "audit", "alert", "clock",
    "local0", "local1", "local2", "local3", "local4", "local5", "local6", "local7",
]
SEVERITIES = ["emerg", "alert", "crit", "err", "warning", "notice", "info", "debug"]

PRI_RE = re.compile(r"^<(\d{1,3})>(.*)$", re.DOTALL)
# 1 TIMESTAMP HOST APP PROCID MSGID SD [MSG]
RFC5424_RE = re.compile(
    r"^1 (\S+) (\S+) (\S+) (\S+) (\S+) (-|(?:\[(?:[^\]\\]|\\.)*\])+)(?: (.*))?$", re.DOTALL
)
# Mmm dd hh:mm:ss HOST TAG[pid]: MSG
RFC3164_RE = re.compile(
    r"^([A-Z][a-z]{2} [ \d]\d \d\d:\d\d:\d\d) (\S+) (?:([^\s:\[]+)(?:\[\d+\])?:? ?)?(.*)$", re.DOTALL
)


# Tasmota sends "DEVICE ESP-TAG: msg" with no <PRI> header
TASMOTA_RE = re.compile(r"^(\S+) (ESP-[^\s:]+):? ?(.*)$", re.DOTALL)


def _nil(value):
    return None if value == "-" else value


def parse(raw, source_ip):
    """Parse a syslog datagram/line into a dict. Never raises; falls back to raw text."""
    text = raw.strip("\x00\r\n ")
    result = {
        "source_ip": source_ip,
        "facility": None,
        "severity": None,
        "host": source_ip,
        "app": None,
        "message": text,
        "raw": text,
    }
    m = PRI_RE.match(text)
    if not m:
        mt = TASMOTA_RE.match(text)
        if mt:
            result["host"], result["app"], result["message"] = mt.groups()
        return result
    pri = int(m.group(1))
    if pri > 191:
        return result
    result["facility"] = FACILITIES[pri >> 3]
    result["severity"] = pri & 7
    body = m.group(2)

    m5 = RFC5424_RE.match(body)
    if m5:
        result["host"] = _nil(m5.group(2)) or source_ip
        result["app"] = _nil(m5.group(3))
        result["message"] = (m5.group(7) or "").lstrip("\ufeff")
        return result

    m3 = RFC3164_RE.match(body)
    if m3:
        result["host"] = m3.group(2)
        result["app"] = m3.group(3)
        result["message"] = m3.group(4)
        return result

    mt = TASMOTA_RE.match(body)   # newer Tasmota: "<PRI>DEVICE ESP-TAG: msg", no timestamp
    if mt:
        result["host"], result["app"], result["message"] = mt.groups()
        return result

    result["message"] = body
    return result
