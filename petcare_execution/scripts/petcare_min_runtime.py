#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


SERVICE = os.getenv("PETCARE_SERVICE", "petcare-ph-l7")
VERSION = os.getenv("PETCARE_VERSION", "ph-l7-min-runtime")
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "10000"))


class Handler(BaseHTTPRequestHandler):
    server_version = "PetCareMinRuntime/1.0"

    def _write_json(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        ts_utc = utc_now_iso()

        if self.path == "/health":
            self._write_json(
                200,
                {
                    "status": "ok",
                    "ts_utc": ts_utc,
                    "service": SERVICE,
                    "version": VERSION,
                },
            )
            return

        if self.path == "/ready":
            self._write_json(
                200,
                {
                    "status": "ready",
                    "ts_utc": ts_utc,
                    "deps": {
                        "runtime": "up",
                    },
                },
            )
            return

        if self.path == "/":
            self._write_json(
                200,
                {
                    "status": "ok",
                    "ts_utc": ts_utc,
                    "service": SERVICE,
                    "version": VERSION,
                    "message": "petcare ph-l7 minimal runtime active",
                },
            )
            return

        self._write_json(
            404,
            {
                "status": "not_found",
                "ts_utc": ts_utc,
                "path": self.path,
            },
        )

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(
        json.dumps(
            {
                "status": "starting",
                "ts_utc": utc_now_iso(),
                "service": SERVICE,
                "version": VERSION,
                "host": HOST,
                "port": PORT,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
