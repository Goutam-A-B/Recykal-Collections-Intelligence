"""Load config.yaml and paths."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.yaml"


def load_config() -> dict[str, Any]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["_root"] = ROOT
    cfg["_data_dir"] = ROOT / cfg.get("paths", {}).get("data_dir", "data")
    cfg["_output_dir"] = ROOT / cfg.get("paths", {}).get("output_dir", "output")
    return cfg


def normalize_header(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_")
