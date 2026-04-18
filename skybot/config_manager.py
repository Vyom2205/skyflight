from __future__ import annotations

import json
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any


_DEFAULT_CONFIG: dict[str, Any] = {
    "admin_role_ids": [],
    "mod_role_ids": [],
    "logging_channel_id": 0,
    "automod_enabled": False,
    "mute_duration_default": 10,  # minutes
}


class ConfigStore:
    """Persistent runtime config store backed by config.json."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.RLock()
        self._config = self._load()

    def _normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(_DEFAULT_CONFIG)
        merged.update({k: v for k, v in data.items() if k in merged})

        for key in ("admin_role_ids", "mod_role_ids"):
            value = merged.get(key, [])
            if not isinstance(value, list):
                value = []
            normalized_values = []
            for item in value:
                try:
                    normalized_values.append(int(item))
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"{key} must contain only integer role IDs (invalid value: {item!r})"
                    ) from exc
            merged[key] = normalized_values

        merged["logging_channel_id"] = int(merged.get("logging_channel_id", 0) or 0)
        merged["automod_enabled"] = bool(merged.get("automod_enabled", False))
        merged["mute_duration_default"] = int(merged.get("mute_duration_default", 10) or 10)
        return merged

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            self.path.write_text(json.dumps(_DEFAULT_CONFIG, indent=2), encoding="utf-8")
            return deepcopy(_DEFAULT_CONFIG)

        with self.path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)

        normalized = self._normalize(loaded if isinstance(loaded, dict) else {})
        self.path.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
        return normalized

    def get(self, key: str) -> Any:
        with self._lock:
            return deepcopy(self._config[key])

    def get_all(self) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self._config)

    def update(self, key: str, value: Any) -> dict[str, Any]:
        with self._lock:
            if key not in _DEFAULT_CONFIG:
                raise KeyError(key)
            updated = deepcopy(self._config)
            updated[key] = value
            self._config = self._normalize(updated)
            self.path.write_text(json.dumps(self._config, indent=2), encoding="utf-8")
            return deepcopy(self._config)

    def add_to_list(self, key: str, value: int) -> dict[str, Any]:
        with self._lock:
            if key not in ("admin_role_ids", "mod_role_ids"):
                raise KeyError(key)
            updated = deepcopy(self._config)
            items = list(updated.get(key, []))
            if value not in items:
                items.append(value)
            updated[key] = items
            self._config = self._normalize(updated)
            self.path.write_text(json.dumps(self._config, indent=2), encoding="utf-8")
            return deepcopy(self._config)

    @property
    def valid_keys(self) -> tuple[str, ...]:
        return tuple(_DEFAULT_CONFIG.keys())
