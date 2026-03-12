import json
from pathlib import Path
import pytest
from analysis.aggregate_results import aggregate


def test_aggregate_fails_on_malformed(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "bad.json").write_text("{oops")
    with pytest.raises(ValueError):
        aggregate(str(raw), str(tmp_path / "agg"))
