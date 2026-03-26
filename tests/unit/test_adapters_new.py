from adapters.iec61499_adapter import IEC61499StyleAdapter
from adapters.ieee1451_adapter import IEEE1451StyleAdapter
from adapters.opcua_adapter import OPCUABridgeAdapter


def sample_payload():
    return {
        "transducer_channel": "sensor_a",
        "measurement": 10.0,
        "timestamp": "2026-01-01T00:00:00Z",
        "teds": {"unit": "C", "manufacturer": "m", "model_number": "x", "serial_number": "1"},
    }


def test_ieee1451_to_canonical():
    adapter = IEEE1451StyleAdapter()
    canonical = adapter.map_to_canonical_model(adapter.normalize_message(adapter.load_source(sample_payload())))
    assert canonical.signal_id == "sensor_a"
    assert canonical.unit == "C"


def test_iec61499_translation_shape():
    source = IEEE1451StyleAdapter()
    target = IEC61499StyleAdapter()
    canonical = source.map_to_canonical_model(source.normalize_message(sample_payload()))
    translated = target.translate_to_target(canonical)
    assert translated["fb_type"] == "AI_BLOCK"


def test_opcua_translation_shape():
    source = IEEE1451StyleAdapter()
    target = OPCUABridgeAdapter(namespace=3)
    canonical = source.map_to_canonical_model(source.normalize_message(sample_payload()))
    translated = target.translate_to_target(canonical)
    assert translated["node_id"] == "ns=3;s=sensor_a"
