#!/usr/bin/env python3
"""Serve ECO-PATH locally with a read-only Brightway calculation API."""

from __future__ import annotations

import argparse
import json
import secrets
import threading
import webbrowser
from dataclasses import dataclass
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from run_brightway import (
    ConfigurationError,
    calculate,
    inspect_brightway_environment,
    load_json,
    validation_summary,
)


ROOT = Path(__file__).resolve().parents[1]
MAX_REQUEST_BYTES = 5 * 1024 * 1024


@dataclass
class ServiceContext:
    mapping: dict[str, Any]
    mapping_path: Path
    token: str
    allow_missing: bool
    calculator: Callable[[dict[str, Any], dict[str, Any], bool, bool], dict[str, Any]]
    environment: dict[str, Any]


def environment_payload(
    mapping: dict[str, Any],
    inspector: Callable[[dict[str, Any]], dict[str, Any]] = inspect_brightway_environment,
) -> dict[str, Any]:
    try:
        return inspector(mapping)
    except ConfigurationError as exc:
        return {"ready": False, "error": str(exc)}


class EcopathRequestHandler(SimpleHTTPRequestHandler):
    server_version = "ECO-PATH-Brightway/1.0"

    def __init__(self, *args: Any, directory: str, context: ServiceContext, **kwargs: Any):
        self.context = context
        super().__init__(*args, directory=directory, **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def list_directory(self, path: str) -> None:
        self.send_error(HTTPStatus.NOT_FOUND)
        return None

    def do_GET(self) -> None:
        if urlparse(self.path).path == "/api/health":
            payload = {
                **self.context.environment,
                "service": "ECO-PATH local Brightway companion",
                "session_token": self.context.token,
                "mapping_file": self.context.mapping_path.name,
                "read_only": True,
            }
            self.send_json(HTTPStatus.OK, payload)
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path not in {"/api/validate", "/api/calculate"}:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Unknown API endpoint"})
            return
        if not self.authorized_request():
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Invalid local service session"})
            return
        if not self.context.environment.get("ready"):
            self.send_json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {"error": self.context.environment.get("error", "Brightway is not ready")},
            )
            return
        try:
            scenario = self.read_json_body()
            if path == "/api/validate":
                self.send_json(
                    HTTPStatus.OK,
                    validation_summary(scenario, self.context.mapping, self.context.allow_missing),
                )
                return
            result = self.context.calculator(
                scenario,
                self.context.mapping,
                self.context.allow_missing,
                False,
            )
            self.send_json(HTTPStatus.OK, result)
        except ConfigurationError as exc:
            self.send_json(HTTPStatus.UNPROCESSABLE_ENTITY, {"error": str(exc)})
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": f"Invalid JSON request: {exc}"})
        except ValueError as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception as exc:
            self.log_error("Brightway calculation failed: %s", exc)
            self.send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "Brightway calculation failed. See the local service terminal for details."},
            )

    def authorized_request(self) -> bool:
        if self.headers.get("X-Ecopath-Token") != self.context.token:
            return False
        origin = self.headers.get("Origin")
        host = self.headers.get("Host")
        if origin and host and origin != f"http://{host}":
            return False
        return self.headers.get("Sec-Fetch-Site", "same-origin") in {"same-origin", "none"}

    def read_json_body(self) -> dict[str, Any]:
        content_type = self.headers.get_content_type()
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Invalid Content-Length") from exc
        if length <= 0 or length > MAX_REQUEST_BYTES:
            raise ValueError("Request body is empty or too large")
        data = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
        return data

    def send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_server(
    host: str,
    port: int,
    mapping: dict[str, Any],
    mapping_path: Path,
    allow_missing: bool = False,
    calculator: Callable[[dict[str, Any], dict[str, Any], bool, bool], dict[str, Any]] = calculate,
    inspector: Callable[[dict[str, Any]], dict[str, Any]] = inspect_brightway_environment,
) -> ThreadingHTTPServer:
    context = ServiceContext(
        mapping=mapping,
        mapping_path=mapping_path,
        token=secrets.token_urlsafe(24),
        allow_missing=allow_missing,
        calculator=calculator,
        environment=environment_payload(mapping, inspector),
    )
    handler = partial(EcopathRequestHandler, directory=str(ROOT), context=context)
    server = ThreadingHTTPServer((host, port), handler)
    server.context = context  # type: ignore[attr-defined]
    return server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", required=True, type=Path, help="Local Brightway mapping JSON")
    parser.add_argument("--host", default="127.0.0.1", help="Loopback host; keep the default")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--allow-missing", action="store_true", help="Allow explicitly documented partial models")
    parser.add_argument("--no-open", action="store_true", help="Do not open the browser automatically")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Refusing to bind outside the local loopback interface")
    mapping = load_json(args.mapping)
    server = create_server(
        args.host,
        args.port,
        mapping,
        args.mapping,
        allow_missing=args.allow_missing,
    )
    url = f"http://{args.host}:{server.server_port}/"
    environment = server.context.environment  # type: ignore[attr-defined]
    print(f"ECO-PATH local Brightway service: {url}")
    print(f"Mapping: {args.mapping}")
    if environment.get("ready"):
        print(f"Brightway project: {environment['project']} (ready)")
    else:
        print(f"Brightway is not ready: {environment.get('error')}")
    print("Press Ctrl-C to stop. No Brightway databases will be modified.")
    if not args.no_open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ECO-PATH local Brightway service.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
