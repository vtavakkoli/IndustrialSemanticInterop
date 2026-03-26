from canonical_model.models import CanonicalMessage
from mappings.engine import MappingEngine


def test_unit_conversion_mapping():
    engine = MappingEngine({"unit_conversion": {"transform": "celsius_to_kelvin", "target_unit": "K"}})
    msg = CanonicalMessage(signal_id="a", value=0.0, unit="C", timestamp="t")
    out = engine.apply(msg)
    assert out.unit == "K"
    assert out.value == 273.15
