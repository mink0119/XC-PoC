#!/usr/bin/env python3
"""Serve the BOLA attacker / learn-traffic lab UI.

Default local bind: 127.0.0.1:8765
Docker / shared PoC host: 0.0.0.0:8765 (e.g. http://192.168.47.81:8765)

Pet Shop remains the target API (often :80 on the same host). Point Target Base URL
in the UI at the Pet Shop or XC VIP — not at this lab port.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import logging
import os
import socketserver
import sys
import webbrowser
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent / "lab"
DEFAULT_PORT = 8765


class LabRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Static lab UI with access logs to stdout (docker compose logs)."""

    def log_message(self, fmt: str, *args) -> None:
        logging.info("%s - %s", self.address_string(), fmt % args)

    def end_headers(self) -> None:
        # Allow embedding / cache-bust during PoC iteration
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    env_host = os.environ.get("LAB_HOST", "127.0.0.1")
    env_port = int(os.environ.get("LAB_PORT", str(DEFAULT_PORT)))

    parser = argparse.ArgumentParser(description="BOLA lab UI (attacker / learn traffic)")
    parser.add_argument("--host", default=env_host, help=f"bind address (default {env_host})")
    parser.add_argument("--port", type=int, default=env_port)
    parser.add_argument("--no-open", action="store_true", help="do not open browser")
    args = parser.parse_args()

    if not (LAB_DIR / "index.html").is_file():
        raise SystemExit(f"missing {LAB_DIR / 'index.html'}")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )

    handler = functools.partial(LabRequestHandler, directory=str(LAB_DIR))
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((args.host, args.port), handler) as httpd:
        display = args.host if args.host not in ("0.0.0.0", "::") else "127.0.0.1"
        url = f"http://{display}:{args.port}/"
        logging.info("Attack lab UI listening on %s:%s", args.host, args.port)
        logging.info("Open %s (or http://<host>:%s/)", url, args.port)
        logging.info("Set Target Base URL to Pet Shop API (e.g. http://192.168.47.81) — not this port")
        if not args.no_open and args.host in ("127.0.0.1", "localhost"):
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("stopped")


if __name__ == "__main__":
    main()
