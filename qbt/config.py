from __future__ import annotations
from typing import Any, Dict
import json
def load_config(path: str) -> Dict[str, Any]:
    path = str(path)
    if path.lower().endswith(('.yml', '.yaml')):
        try:
            import yaml  # type: ignore
        except Exception as e:
            raise RuntimeError("PyYAML is required for YAML configs. Install with `pip install pyyaml`.") from e
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    elif path.lower().endswith('.json'):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise ValueError("Unsupported config format. Use .yaml/.yml or .json")
