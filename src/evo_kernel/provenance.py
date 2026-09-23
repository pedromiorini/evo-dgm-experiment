"""Proveniência verificável para variantes e mutações."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

from .integrity import canonical_json, sha256_bytes


class ProvenanceError(ValueError):
    """Metadado de lineage inválido ou adulterado."""


@dataclass(frozen=True)
class LineageRecord:
    variant_id: str
    parent_id: str | None
    generation: int
    seed: int
    genome_hash: str
    diff_hash: str | None
    timestamp: str
    record_hash: str

    @classmethod
    def create(
        cls,
        *,
        variant_id: str,
        parent_id: str | None,
        generation: int,
        seed: int,
        genome_hash: str,
        diff_hash: str | None,
    ) -> "LineageRecord":
        if generation < 0:
            raise ProvenanceError("generation deve ser não negativa")
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "variant_id": variant_id,
            "parent_id": parent_id,
            "generation": generation,
            "seed": seed,
            "genome_hash": genome_hash,
            "diff_hash": diff_hash,
            "timestamp": timestamp,
        }
        return cls(**payload, record_hash=sha256_bytes(canonical_json(payload)))

    def verify(self) -> None:
        payload: dict[str, Any] = asdict(self)
        record_hash = payload.pop("record_hash")
        if sha256_bytes(canonical_json(payload)) != record_hash:
            raise ProvenanceError("hash de provenance não confere")
