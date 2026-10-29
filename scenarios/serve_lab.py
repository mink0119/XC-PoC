#!/usr/bin/env python3
"""Serve the local BOLA attacker lab UI.

Pet Shop (e.g. 192.168.47.81) is only the target API.
Open this UI on your laptop, then point Target Base URL at the Pet Shop.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import sys
import webbrowser
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent / "lab"
DEFAULT_PORT = 8765


def main():
    parser = argparse.ArgumentParser(description="Local BOLA lab UI (attacker side)")
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-open", action="store_true", help="do not open browser")
    args = parser.parse_args()

    if not (LAB_DIR / "index.html").is_file():
        raise SystemExit(f"missing {LAB_DIR / 'index.html'}")

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(LAB_DIR))
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((args.host, args.port), handler) as httpd:
        url = f"http://{args.host}:{args.port}/"
        print(f"Local attacker lab: {url}")
        print("Target API stays on Pet Shop (e.g. http://192.168.47.81) — set it in the UI.")
        if not args.no_open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped", file=sys.stderr)


if __name__ == "__main__":
    main()
