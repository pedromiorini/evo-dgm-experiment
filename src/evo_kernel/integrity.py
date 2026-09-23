"""Integridade local verificável; não alegamos imutabilidade absoluta."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> bytes:
    """Serializa dados de forma determinística para hashing e logs."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class HashChain:
    """Cadeia append-only lógica para detectar edição, reorder e truncamento."""

    def __init__(self, genesis: str = "0" * 64) -> None:
        if len(genesis) != 64:
            raise ValueError("genesis deve ser um SHA-256 hexadecimal")
        self._head = genesis
        self._entries: list[dict[str, Any]] = []

    @property
    def head(self) -> str:
        return self._head

    @property
    def entries(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._entries)

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        payload = {"previous_hash": self._head, "event": event}
        entry = {**payload, "entry_hash": sha256_bytes(canonical_json(payload))}
        self._entries.append(entry)
        self._head = entry["entry_hash"]
        return entry

    @staticmethod
    def verify(entries: list[dict[str, Any]], genesis: str = "0" * 64) -> bool:
        previous = genesis
        for entry in entries:
            if entry.get("previous_hash") != previous:
                return False
            payload = {"previous_hash": entry["previous_hash"], "event": entry.get("event")}
            if entry.get("entry_hash") != sha256_bytes(canonical_json(payload)):
                return False
            previous = entry["entry_hash"]
        return True
