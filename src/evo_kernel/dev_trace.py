"""DEV_TRACE do PATCH 7: feedback descritivo, nunca política ou instrução."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

from .integrity import canonical_json, sha256_bytes


class DevTraceError(ValueError):
    """DEV_TRACE inválido ou contendo campos protegidos."""


_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
)
_PROTECTED_FIELD_NAMES = frozenset({"selection", "final", "holdout", "credentials", "secrets"})
_MAX_CONTENT = 4096


def sanitize_text(content: str) -> str:
    if not isinstance(content, str):
        raise DevTraceError("conteúdo deve ser texto")
    sanitized = content[:_MAX_CONTENT]
    for pattern in _SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


@dataclass(frozen=True)
class DevTraceEntry:
    source_variant_id: str
    generation: int
    producer: str
    content: str
    content_hash: str
    timestamp: str
    trust_class: str = "UNTRUSTED_DATA"

    @classmethod
    def create(cls, *, source_variant_id: str, generation: int, producer: str, content: str) -> "DevTraceEntry":
        sanitized = sanitize_text(content)
        if not source_variant_id or generation < 0 or not producer:
            raise DevTraceError("metadados DEV_TRACE inválidos")
        timestamp = datetime.now(timezone.utc).isoformat()
        return cls(
            source_variant_id=source_variant_id,
            generation=generation,
            producer=producer,
            content=sanitized,
            content_hash=sha256_bytes(sanitized.encode("utf-8")),
            timestamp=timestamp,
        )

    def validate(self) -> None:
        if self.trust_class != "UNTRUSTED_DATA":
            raise DevTraceError("DEV_TRACE não pode ter autoridade instrucional")
        if sha256_bytes(self.content.encode("utf-8")) != self.content_hash:
            raise DevTraceError("hash DEV_TRACE inconsistente")


@dataclass(frozen=True)
class DevTrace:
    entries: tuple[DevTraceEntry, ...]

    def __post_init__(self) -> None:
        for entry in self.entries:
            entry.validate()

    @classmethod
    def from_events(cls, events: tuple[dict[str, Any], ...]) -> "DevTrace":
        entries: list[DevTraceEntry] = []
        for event in events:
            forbidden = _PROTECTED_FIELD_NAMES.intersection(event)
            if forbidden:
                raise DevTraceError(f"campos protegidos não entram em DEV_TRACE: {sorted(forbidden)}")
            entries.append(DevTraceEntry.create(
                source_variant_id=str(event.get("source_variant_id", "")),
                generation=int(event.get("generation", -1)),
                producer=str(event.get("producer", "")),
                content=str(event.get("content", "")),
            ))
        return cls(tuple(entries))

    def as_untrusted_history(self) -> tuple[dict[str, Any], ...]:
        """Forma serializável sem qualquer campo de seleção ou política."""
        return tuple({
            "source_variant_id": entry.source_variant_id,
            "generation": entry.generation,
            "producer": entry.producer,
            "content": entry.content,
            "content_hash": entry.content_hash,
            "timestamp": entry.timestamp,
            "trust_class": "UNTRUSTED_DATA",
        } for entry in self.entries)
