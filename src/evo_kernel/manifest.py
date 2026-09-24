"""Manifesto congelado: política, custo e ambiente não podem mudar silenciosamente."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .integrity import canonical_json, sha256_bytes


class ManifestError(ValueError):
    """Manifesto ausente, incompleto ou inconsistente."""


EXPLORATORY_REQUIRED_FIELDS = frozenset(
    {
        "experiment_id", "protocol_version", "mode", "hypothesis",
        "primary_metric", "cost_estimand", "max_total_cost", "final_feedback",
        "llm", "security_profile",
    }
)
CONFIRMATORY_REQUIRED_FIELDS = EXPLORATORY_REQUIRED_FIELDS | frozenset(
    {
        "freeze_timestamp", "claim_level", "sesoi", "alpha", "power",
        "contrasts", "baselines", "finalist_rule", "seeds", "domain",
        "pcf", "kernel_hash", "dependency_hashes", "environment", "final_policy",
    }
)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class FrozenManifest:
    data: Mapping[str, Any]
    manifest_hash: str

    @classmethod
    def freeze(cls, data: Mapping[str, Any]) -> "FrozenManifest":
        payload = dict(data)
        required = CONFIRMATORY_REQUIRED_FIELDS if payload.get("mode") == "CONFIRMATORY" else EXPLORATORY_REQUIRED_FIELDS
        missing = sorted(required - payload.keys())
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
        frozen = _freeze(payload)
        digest = sha256_bytes(canonical_json(frozen))
        return cls(data=frozen, manifest_hash=digest)

    def verify(self) -> None:
        if sha256_bytes(canonical_json(self.data)) != self.manifest_hash:
            raise ManifestError("manifest_hash não confere")

    def unchanged_from(self, other: "FrozenManifest") -> bool:
        return self.manifest_hash == other.manifest_hash
