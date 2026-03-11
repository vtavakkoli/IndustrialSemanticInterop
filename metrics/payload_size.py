import json


def payload_size_bytes(payload: dict) -> int:
    return len(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
