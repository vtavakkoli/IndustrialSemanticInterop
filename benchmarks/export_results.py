import json
from pathlib import Path


def export_json(result: dict, out_dir: str):
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    name = f"{result['scenario_id']}__run{result['run_index']:03d}.json"
    path = p / name
    path.write_text(json.dumps(result, indent=2))
    return str(path)
