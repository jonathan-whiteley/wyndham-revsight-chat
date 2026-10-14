"""Workspace-specific settings: catalog, schema and Genie space IDs.

On Databricks Apps these arrive as environment variables (app.yaml). For local
runs and tests, anything not set in the environment is read from the repo's
config.env, so there is exactly one place to change them.
"""

import os
from pathlib import Path
from typing import Dict

CONFIG_FILE = Path(__file__).resolve().parents[2] / "config.env"


def _read_config_file() -> Dict[str, str]:
    if not CONFIG_FILE.is_file():
        return {}
    values = {}
    for line in CONFIG_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


_FILE = _read_config_file()


def get(key: str) -> str:
    """Environment first, then config.env. Raises if neither has a value."""
    value = os.environ.get(key) or _FILE.get(key, "")
    if not value:
        raise RuntimeError(f"{key} is not set: add it to config.env (local) or app.yaml env (deployed)")
    return value


CATALOG = get("CATALOG")
SCHEMA = get("SCHEMA")


def fqn(name: str) -> str:
    """Fully qualified Unity Catalog name for an object in the configured schema."""
    return f"{CATALOG}.{SCHEMA}.{name}"
