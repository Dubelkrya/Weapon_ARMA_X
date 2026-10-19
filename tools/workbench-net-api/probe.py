"""Read-only Workbench NET API probe. Loopback only; stdlib only."""
import argparse
import json
import socket
import struct
import uuid
from datetime import datetime, timezone
from pathlib import Path

MAX_FRAME = 1024 * 1024
EXPECTED_VERSION = "WAX_ReadOnlyNetApi/v6"


def validate_payload(payload):
    if payload.get("endpoint") != EXPECTED_VERSION:
        raise ValueError("Expected v6; loaded " + str(payload.get("endpoint")))
    count = payload.get("selectedCount")
    entities = payload.get("entities", [])
    if not isinstance(count, int) or count < 0 or not isinstance(entities, list):
        raise ValueError("Invalid selection metadata")
    if len(entities) != min(count, 8):
        raise ValueError("Missing serialized entities")
    for entity in entities:
        if not isinstance(entity, dict) or not entity.get("firstSelectedName"):
            raise ValueError("Empty or invalid entity serialization")
        fields = entity.get("fields", [])
        if not isinstance(fields, list) or not fields:
            raise ValueError("Missing structured fields")
        for field in fields:
            if not isinstance(field, dict) or not {"path", "field", "valueType", "status"}.issubset(field):
                raise ValueError("Invalid field serialization")
            if field["status"] not in ("ok", "absent", "read-failed"):
                raise ValueError("Unknown field status")


def frame(value):
    data = value.encode("utf-8")
    if len(data) > MAX_FRAME:
        raise ValueError("Request exceeds frame limit")
    return struct.pack("<I", len(data)) + data


def receive_exact(connection, size):
    result = bytearray()
    while len(result) < size:
        chunk = connection.recv(size - len(result))
        if not chunk:
            raise EOFError("Workbench closed an incomplete response")
        result.extend(chunk)
    return bytes(result)


def receive_string(connection):
    size = struct.unpack("<I", receive_exact(connection, 4))[0]
    if size > MAX_FRAME:
        raise ValueError("Response exceeds frame limit")
    return receive_exact(connection, size).decode("utf-8")


def call(port, endpoint, nonce=None):
    # Deliberately no arbitrary APIFunc option: never call mutation endpoints.
    if endpoint not in ("IsWorkbenchRunning", "IsWorldEditorRunning", "WAX_ReadOnlyNetApi"):
        raise ValueError("Endpoint is not read-only allowlisted")
    payload = {"APIFunc": endpoint}
    if nonce is not None:
        payload["nonce"] = nonce
    packet = struct.pack("<I", 1) + frame("WeaponXReadOnlyProbe")
    packet += frame("JsonRPC") + frame(json.dumps(payload))
    with socket.create_connection(("127.0.0.1", port), timeout=3) as connection:
        connection.settimeout(3)
        connection.sendall(packet)
        error = receive_string(connection)
        raw = receive_string(connection)
    return {"endpoint": endpoint, "error_code": error,
            "payload": json.loads(raw) if raw else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5775)
    parser.add_argument("--custom", action="store_true", help="Also test the loaded WAX handler")
    parser.add_argument("--snapshot", action="store_true", help="Save successful v5 results in Weapon X artifacts")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")
    failed = False
    results = []
    endpoints = ["IsWorkbenchRunning", "IsWorldEditorRunning"]
    if args.custom or args.snapshot:
        endpoints.append("WAX_ReadOnlyNetApi")
    for endpoint in endpoints:
        nonce = uuid.uuid4().hex if endpoint == "WAX_ReadOnlyNetApi" else None
        try:
            result = call(args.port, endpoint, nonce)
            if result["error_code"] != "Ok":
                raise ValueError("API error: " + result["error_code"])
            if nonce is not None:
                result["nonce_matches"] = isinstance(result["payload"], dict) and result["payload"].get("nonce") == nonce
                failed |= not result["nonce_matches"]
                if not result["nonce_matches"]:
                    raise ValueError("Nonce mismatch")
                validate_payload(result["payload"])
            results.append(result)
            print(json.dumps(result, ensure_ascii=False))
        except (OSError, ValueError, EOFError) as exc:
            print(json.dumps({"endpoint": endpoint, "transport_error": str(exc)}, ensure_ascii=False))
            failed = True
            break
    if args.snapshot and not failed:
        directory = Path(__file__).resolve().parents[2] / "artifacts" / "workbench-net-api"
        directory.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        destination = directory / (now.strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8] + ".json")
        with destination.open("x", encoding="utf-8") as output:
            json.dump({"captured_at_utc": now.isoformat(), "results": results}, output, ensure_ascii=False, indent=2)
        print(json.dumps({"snapshot": str(destination)}, ensure_ascii=False))
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
