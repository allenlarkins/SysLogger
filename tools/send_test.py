"""Send sample syslog messages to a running SysLogger."""
import argparse
import socket

SAMPLES = [
    "<34>Oct 17 10:15:32 mymachine su: 'su root' failed for lonvick on /dev/pts/8",
    "<165>1 2026-10-17T10:15:32.003Z router1 sshd 1234 ID47 - Accepted password for admin",
    "<11>1 2026-10-17T10:15:33Z esp-livingroom firmware - - [meta k=\"v\"] Sensor read failed",
    "<14>Oct 17 10:15:34 nas kernel: disk sda healthy",
    "<191>Oct  7 10:15:35 host1 app[99]: debug trace",
    "plain text with no priority header",
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5514)
    p.add_argument("--tcp", action="store_true")
    args = p.parse_args()

    if args.tcp:
        with socket.create_connection((args.host, args.port)) as s:
            for m in SAMPLES:
                s.sendall(m.encode() + b"\n")
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            for m in SAMPLES:
                s.sendto(m.encode(), (args.host, args.port))
    print(f"Sent {len(SAMPLES)} messages via {'TCP' if args.tcp else 'UDP'}")


if __name__ == "__main__":
    main()
