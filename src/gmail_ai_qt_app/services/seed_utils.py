from __future__ import annotations

from collections.abc import Iterable


def normalize_seed_value(value: str) -> str:
    return "".join(ch for ch in (value or "").lower() if ch.isalnum())


def sanitize_seed_values(values: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for value in values:
        item = normalize_seed_value(value)
        if not item or item in seen:
            continue
        seen.add(item)
        normalized.append(item)

    return normalized
