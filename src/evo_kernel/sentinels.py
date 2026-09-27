"""Sentinels kernel-only: existência de path não constitui evidência de acesso."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass


class SentinelError(ValueError):
    """Sentinel inválido, duplicado ou observação inconsistente."""


@dataclass(frozen=True)
class Sentinel:
    sentinel_id: str
    protected_path: str
    secret_digest: str

    def public_record(self) -> dict[str, str]:
        return {"sentinel_id": self.sentinel_id, "protected_path": self.protected_path}


@dataclass(frozen=True)
class SentinelObservation:
    sentinel_id: str
    attempted: bool
    opened: bool
    observed_value_digest: str | None
    exfiltrated: bool = False

    def validate(self) -> None:
        if not self.sentinel_id:
            raise SentinelError("observação sem sentinel_id")
        if not self.attempted and (self.opened or self.observed_value_digest or self.exfiltrated):
            raise SentinelError("observação inconsistente sem tentativa")


class SentinelRegistry:
    """Mantém o segredo somente no domínio confiável e compara por digest."""

    def __init__(self) -> None:
        self._secrets: dict[str, bytes] = {}
        self._sentinels: dict[str, Sentinel] = {}

    def issue(self, sentinel_id: str, protected_path: str) -> Sentinel:
        if not sentinel_id or not protected_path or sentinel_id in self._sentinels:
            raise SentinelError("sentinel inválido ou duplicado")
        secret = secrets.token_bytes(32)
        digest = hashlib.sha256(secret).hexdigest()
        sentinel = Sentinel(sentinel_id, protected_path, digest)
        self._secrets[sentinel_id] = secret
        self._sentinels[sentinel_id] = sentinel
        return sentinel

    def observe(self, observation: SentinelObservation) -> str:
        observation.validate()
        sentinel = self._sentinels.get(observation.sentinel_id)
        if sentinel is None:
            raise SentinelError("sentinel desconhecido")
        if not observation.attempted or not observation.opened:
            return "BLOCKED"
        if observation.observed_value_digest == sentinel.secret_digest:
            return "DETECTED"
        return "UNVERIFIED"

    def public_records(self) -> tuple[dict[str, str], ...]:
        return tuple(sentinel.public_record() for sentinel in self._sentinels.values())
