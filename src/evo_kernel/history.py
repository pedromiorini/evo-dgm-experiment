"""Montagem estrutural de contexto histórico não confiável."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from .integrity import sha256_bytes


@dataclass(frozen=True)
class HistoricalRecord:
    source_variant_id: str
    generation: int
    producer: str
    content: str
    content_hash: str
    timestamp: str
    trust_class: str = "UNTRUSTED_DATA"

    @classmethod
    def create(cls, *, source_variant_id: str, generation: int, producer: str, content: str) -> "HistoricalRecord":
        timestamp = datetime.now(timezone.utc).isoformat()
        return cls(
            source_variant_id=source_variant_id,
            generation=generation,
            producer=producer,
            content=content,
            content_hash=sha256_bytes(content.encode("utf-8")),
            timestamp=timestamp,
        )

    def validate(self) -> None:
        if self.trust_class != "UNTRUSTED_DATA":
            raise ValueError("histórico não pode receber classe de confiança instrucional")
        if sha256_bytes(self.content.encode("utf-8")) != self.content_hash:
            raise ValueError("hash do histórico não confere")


def build_prompt_context(*, system_policy: str, current_task: str, allowed_actions: tuple[str, ...], history: tuple[HistoricalRecord, ...]) -> dict:
    """Retorna campos separados; histórico nunca é mesclado à política."""
    for record in history:
        record.validate()
    return {
        "SYSTEM_POLICY": system_policy,
        "CURRENT_TASK": current_task,
        "ALLOWED_ACTIONS": list(allowed_actions),
        "UNTRUSTED_HISTORY": [asdict(record) for record in history],
    }
