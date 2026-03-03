#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone

def ts():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SERVICE = os.environ.get("PETCARE_SERVICE", "petcare")
VERSION = os.environ.get("PETCARE_VERSION", "dev")

class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, payload):
        body = (json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {
                "status": "ok",
                "service": SERVICE,
                "ts_utc": ts(),
                "version": VERSION
            })
            return
        if self.path == "/ready":
            self.send_json(200, {
                "status": "ready",
                "deps": {"db": "unknown", "queue": "unknown"},
                "ts_utc": ts()
            })
            return
        self.send_json(404, {"status": "not_found", "ts_utc": ts()})

    def log_message(self, format, *args):
        return

def main():
    host = "127.0.0.1"
    port = 8099
    server = HTTPServer((host, port), Handler)
    print(f"Health server listening on {host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    main()
