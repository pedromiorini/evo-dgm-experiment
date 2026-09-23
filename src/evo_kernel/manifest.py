"""Manifesto congelado: política, custo e ambiente não podem mudar silenciosamente."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .integrity import canonical_json, sha256_bytes


class ManifestError(ValueError):
    """Manifesto ausente, incompleto ou inconsistente."""


REQUIRED_FIELDS = frozenset(
    {
        "experiment_id",
        "protocol_version",
        "mode",
        "hypothesis",
        "primary_metric",
        "cost_estimand",
        "max_total_cost",
        "final_feedback",
        "llm",
        "security_profile",
    }
)


@dataclass(frozen=True)
class FrozenManifest:
    data: dict[str, Any]
    manifest_hash: str

    @classmethod
    def freeze(cls, data: Mapping[str, Any]) -> "FrozenManifest":
        payload = dict(data)
        missing = sorted(REQUIRED_FIELDS - payload.keys())
        if missing:
            raise ManifestError(f"campos obrigatórios ausentes: {', '.join(missing)}")
        if payload.get("final_feedback") is not False:
            raise ManifestError("final_feedback deve ser false")
        if payload.get("mode") not in {"EXPLORATORY", "CONFIRMATORY"}:
            raise ManifestError("mode inválido")
        if not isinstance(payload.get("llm"), Mapping):
            raise ManifestError("llm deve ser um objeto estruturado")
        if not isinstance(payload.get("security_profile"), Mapping):
            raise ManifestError("security_profile deve ser um objeto estruturado")
        digest = sha256_bytes(canonical_json(payload))
        return cls(data=payload, manifest_hash=digest)

    def verify(self) -> None:
        if sha256_bytes(canonical_json(self.data)) != self.manifest_hash:
            raise ManifestError("manifest_hash não confere")

    def unchanged_from(self, other: "FrozenManifest") -> bool:
        return self.manifest_hash == other.manifest_hash
