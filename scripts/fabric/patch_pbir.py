#!/usr/bin/env python3
"""Offline replacement of existing JSON properties in selected PBIR parts."""

import argparse
import base64
import copy
import json
import sys
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def checked_child(parent, key):
    if isinstance(parent, dict) and isinstance(key, str):
        return parent[key]
    if isinstance(parent, list) and type(key) is int and 0 <= key < len(parent):
        return parent[key]
    raise ValueError("Key must address an existing object property or array index")


def apply_plan(document, plan):
    result = copy.deepcopy(document)
    value = result.get("definition", result)
    if not isinstance(value, dict) or not isinstance(value.get("parts"), list):
        raise ValueError("Expected definition.parts")
    parts = {}
    for part in value["parts"]:
        path = part.get("path")
        if not isinstance(path, str) or not path or path in parts:
            raise ValueError("Missing or duplicate part path")
        parts[path] = part
    if not isinstance(plan, list) or not plan:
        raise ValueError("Plan must be a nonempty list")
    decoded = {}
    touched = set()
    for change in plan:
        if not isinstance(change, dict) or set(change) != {"part", "keys", "old", "new"}:
            raise ValueError("Each change needs part, keys, old, new")
        path, keys = change["part"], change["keys"]
        if not isinstance(path, str) or not isinstance(keys, list) or not keys:
            raise ValueError("Invalid part path or property keys")
        if any(not isinstance(k, str) and type(k) is not int for k in keys):
            raise ValueError("Property keys must be strings or integer indices")
        marker = (path, tuple(keys))
        if marker in touched:
            raise ValueError("A property may be replaced only once per plan")
        touched.add(marker)
        if path not in decoded:
            part = parts[path]
            if part.get("payloadType") != "InlineBase64":
                raise ValueError("Only InlineBase64 payloads are supported")
            decoded[path] = json.loads(base64.b64decode(part["payload"], validate=True))
        parent = decoded[path]
        for key in keys[:-1]:
            parent = checked_child(parent, key)
        old = checked_child(parent, keys[-1])
        # JSON bool and number must not be treated as interchangeable old values.
        if type(old) is not type(change["old"]) or old != change["old"]:
            raise ValueError("Old-value mismatch; inspect the private plan")
        parent[keys[-1]] = copy.deepcopy(change["new"])
    for path, obj in decoded.items():
        raw = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
        parts[path]["payload"] = base64.b64encode(raw).decode("ascii")
    return result, sorted(decoded)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        raise ValueError("Output must be a new file")
    result, paths = apply_plan(read_json(args.source), read_json(args.plan))
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    # Part paths may identify private objects; only print the count by default.
    print(f"Patched {len(paths)} part(s); unselected payloads preserved")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError, IndexError, AttributeError):
        print("Patch rejected; check private inputs, keys and old values", file=sys.stderr)
        sys.exit(2)
