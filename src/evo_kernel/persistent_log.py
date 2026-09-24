"""Log kernel persistente, hash-chained e apenas tamper-evident local."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterator

from .integrity import canonical_json, sha256_bytes


GENESIS_HASH = "0" * 64


class LogIntegrityError(RuntimeError):
    """Arquivo ausente, malformado ou cadeia hash inconsistente."""


class KernelLog:
    """Append-only lógico em JSONL; não alegamos imutabilidade física."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def _iter_raw(self) -> Iterator[dict[str, Any]]:
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                for number, raw in enumerate(handle, start=1):
                    if not raw.strip():
                        continue
                    try:
                        value = json.loads(raw)
                    except json.JSONDecodeError as exc:
                        raise LogIntegrityError(f"JSON inválido na linha {number}") from exc
                    if not isinstance(value, dict):
                        raise LogIntegrityError(f"entrada não é objeto na linha {number}")
                    yield value
        except OSError as exc:
            raise LogIntegrityError(f"falha ao ler log: {self.path}") from exc

    def _last_hash(self) -> str:
        last = GENESIS_HASH
        for entry in self._iter_raw():
            last = entry.get("entry_hash", "")
        return last

    def append(self, event: str, payload: dict[str, Any]) -> dict[str, Any]:
        previous_hash = self._last_hash()
        record = {"timestamp": time.time(), "event": event, "payload": payload}
        entry_hash = sha256_bytes(canonical_json({"previous_hash": previous_hash, **record}))
        entry = {"previous_hash": previous_hash, **record, "entry_hash": entry_hash}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
        return entry

    def verify_chain(self) -> None:
        previous_hash = GENESIS_HASH
        for number, entry in enumerate(self._iter_raw(), start=1):
            if entry.get("previous_hash") != previous_hash:
                raise LogIntegrityError(f"cadeia quebrada na entrada {number}")
            required = {"timestamp", "event", "payload", "entry_hash"}
            if not required.issubset(entry):
                raise LogIntegrityError(f"campos ausentes na entrada {number}")
            expected = sha256_bytes(canonical_json({
                "previous_hash": entry["previous_hash"],
                "timestamp": entry["timestamp"],
                "event": entry["event"],
                "payload": entry["payload"],
            }))
            if entry["entry_hash"] != expected:
                raise LogIntegrityError(f"hash inconsistente na entrada {number}")
            previous_hash = entry["entry_hash"]

    def integrity_status(self) -> str:
        try:
            self.verify_chain()
        except LogIntegrityError:
            return "TAMPERED"
        return "TAMPER_EVIDENT_LOCAL_ONLY"

    @property
    def chain_head_hash(self) -> str:
        return self._last_hash()

    def all_entries(self) -> list[dict[str, Any]]:
        return list(self._iter_raw())
