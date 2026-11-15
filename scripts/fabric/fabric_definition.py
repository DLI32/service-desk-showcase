#!/usr/bin/env python3
"""Parameterized Fabric definitions; compare is offline, get/update use the API."""

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_ROOT = "https://api.fabric.microsoft.com/v1/"
RESOURCE = "https://api.fabric.microsoft.com"
KINDS = ("reports", "semanticModels", "notebooks")


class OperationError(RuntimeError):
    """A sanitized error without response bodies or credentials."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Authorization must never follow a server-provided redirect.
        return None


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def definition(document):
    if not isinstance(document, dict):
        raise ValueError("Expected a definition object")
    value = document.get("definition", document)
    if not isinstance(value, dict) or not isinstance(value.get("parts"), list):
        raise ValueError("Expected definition.parts")
    return value


def fingerprint(document):
    result = {}
    for part in definition(document)["parts"]:
        path = part.get("path")
        if not isinstance(path, str) or not path or path in result:
            raise ValueError("Missing or duplicate part path")
        if part.get("payloadType") != "InlineBase64":
            raise ValueError("Only InlineBase64 payloads are supported")
        raw = base64.b64decode(part["payload"], validate=True)
        try:
            value = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            pass
        else:
            raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")
        result[path] = hashlib.sha256(raw).hexdigest()
    return result


def changes(left, right):
    return sorted(key for key in set(left) | set(right)
                  if left.get(key) != right.get(key))


def ensure_new(path):
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise ValueError("Output already exists; choose a new file")
    if not path.parent.is_dir():
        raise ValueError("Create the output parent directory first")


def save_new(path, value):
    # Exclusive creation prevents accidental replacement of a private backup.
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def segment(value):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ValueError("API identifiers must be nonempty path segments")
    return value


def retry_delay(headers, default=3):
    try:
        return max(1, min(30, int(headers.get("Retry-After", default))))
    except (ValueError, TypeError):
        return default


class FabricClient:
    def __init__(self, az="az", timeout=60, poll_timeout=1800):
        self.az = az
        self.timeout = timeout
        self.poll_timeout = poll_timeout
        self.opener = urllib.request.build_opener(NoRedirect())

    def access_token(self):
        try:
            result = subprocess.run(
                [self.az, "account", "get-access-token", "--resource", RESOURCE,
                 "--query", "accessToken", "-o", "tsv"],
                capture_output=True, text=True, check=True, timeout=self.timeout,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise OperationError("Azure CLI authentication failed; check login locally") from exc
        value = result.stdout.strip()
        if not value:
            raise OperationError("Azure CLI returned no access token")
        return value

    def request(self, path, method="GET", body=None):
        # All paths are constructed here; no Location or arbitrary host is used.
        if path.startswith("/") or ".." in path or ":" in path:
            raise ValueError("Invalid relative API path")
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            API_ROOT + path, data=data, method=method,
            headers={"Authorization": "Bearer " + self.access_token(),
                     "Content-Type": "application/json"},
        )
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                raw = response.read()
                return response.status, response.headers, json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            # API bodies may echo private identifiers or payloads. Do not log them.
            raise OperationError(f"Fabric HTTP {exc.code}; inspect private service diagnostics") from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise OperationError("Network failure; inspect operation state before resubmitting") from exc

    def operation(self, path, body, needs_result):
        status, headers, result = self.request(path, "POST", body)
        if status != 202:
            return result
        op_id = headers.get("x-ms-operation-id")
        if not op_id:
            raise OperationError("Accepted operation has no operation id; inspect service state")
        poll_path = "operations/" + segment(op_id)
        # The private id is intentionally not printed to shared output.
        deadline = time.monotonic() + self.poll_timeout
        delay = retry_delay(headers)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise OperationError("Polling timed out; do not automatically resubmit")
            time.sleep(min(delay, remaining))
            if time.monotonic() >= deadline:
                raise OperationError("Polling timed out; inspect service state")
            _, headers, state = self.request(poll_path)
            if not isinstance(state, dict):
                raise OperationError("Invalid operation status response")
            phase = state.get("status")
            if phase == "Succeeded":
                return self.request(poll_path + "/result")[2] if needs_result else state
            if phase in ("Failed", "Cancelled", "Canceled"):
                raise OperationError("Fabric operation did not succeed; inspect private diagnostics")
            delay = retry_delay(headers)

    def get(self, endpoint, kind):
        body = {"format": "PBIR"} if kind == "reports" else (
            {"format": "ipynb"} if kind == "notebooks" else {})
        result = self.operation(endpoint + "/getDefinition", body, needs_result=True)
        fingerprint(result)
        return result


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Must be positive")
    return number


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="action", required=True)
    compare = commands.add_parser("compare", help="Offline per-part payload comparison")
    compare.add_argument("left", type=Path)
    compare.add_argument("right", type=Path)
    for action in ("get", "update"):
        command = commands.add_parser(action)
        command.add_argument("kind", choices=KINDS)
        command.add_argument("--workspace", required=True)
        command.add_argument("--item", required=True)
        command.add_argument("--az", default="az", help="Azure CLI executable")
        command.add_argument("--timeout", type=positive, default=60)
        command.add_argument("--poll-timeout", type=positive, default=1800)
        if action == "get":
            command.add_argument("--output", required=True, type=Path)
        else:
            command.add_argument("--input", required=True, type=Path)
            command.add_argument("--baseline", required=True, type=Path,
                                 help="Unmodified editing baseline for concurrency check")
            command.add_argument("--readback", required=True, type=Path)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    if args.action == "compare":
        delta = changes(fingerprint(load(args.left)), fingerprint(load(args.right)))
        print(json.dumps(delta, ensure_ascii=False, indent=2))
        return 1 if delta else 0
    endpoint = (f"workspaces/{segment(args.workspace)}/{args.kind}/"
                f"{segment(args.item)}")
    target = args.output if args.action == "get" else args.readback
    ensure_new(target)
    client = FabricClient(args.az, args.timeout, args.poll_timeout)
    if args.action == "get":
        save_new(target, client.get(endpoint, args.kind))
        print("Definition saved to private output")
        return 0
    candidate = load(args.input)
    expected = fingerprint(candidate)
    baseline = fingerprint(load(args.baseline))
    current = fingerprint(client.get(endpoint, args.kind))
    if changes(baseline, current):
        raise OperationError("Remote definition differs from baseline; merge before updating")
    client.operation(endpoint + "/updateDefinition",
                     {"definition": definition(candidate)}, needs_result=False)
    actual = client.get(endpoint, args.kind)
    save_new(args.readback, actual)
    delta = changes(expected, fingerprint(actual))
    if delta:
        print(json.dumps(delta, ensure_ascii=False, indent=2))
        raise OperationError("Readback differs; review normalization or content changes")
    print("Definition payload readback verified; validate data and report behavior separately")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OperationError, ValueError, OSError, KeyError, TypeError) as exc:
        # Avoid response bodies, local paths, and definition content in shared logs.
        if isinstance(exc, OperationError):
            print(str(exc), file=sys.stderr)
        else:
            print("Invalid input or local file operation; inspect private files", file=sys.stderr)
        sys.exit(2)
