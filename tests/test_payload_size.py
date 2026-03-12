from metrics.payload_size import payload_size_bytes


def test_payload_size_uses_serialization():
    a = {"x": "a"}
    b = {"x": "a" * 100}
    assert payload_size_bytes(b) > payload_size_bytes(a)
