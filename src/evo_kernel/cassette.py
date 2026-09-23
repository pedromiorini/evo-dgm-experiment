"""Cassettes tamper-evident para replay; não fazem chamadas ao provedor."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Any

from .integrity import canonical_json, sha256_bytes


class CassetteError(ValueError):
    """Cassette inválido ou adulterado."""


@dataclass(frozen=True)
class Cassette:
    cassette_id: str
    provider: str
    model: str
    version: str
    request: dict[str, Any]
    response: dict[str, Any]
    tokens: int
    cost: Decimal
    cassette_hash: str

    @classmethod
    def create(
        cls, *, cassette_id: str, provider: str, model: str, version: str,
        request: dict[str, Any], response: dict[str, Any], tokens: int,
        cost: Decimal | str | float,
    ) -> "Cassette":
        if not cassette_id or tokens < 0:
            raise CassetteError("identidade e tokens inválidos")
        cost_decimal = Decimal(str(cost))
        payload = {
            "cassette_id": cassette_id, "provider": provider, "model": model,
            "version": version, "request": request, "response": response,
            "tokens": tokens, "cost": str(cost_decimal),
        }
        return cls(
            cassette_id=cassette_id,
            provider=provider,
            model=model,
            version=version,
            request=request,
            response=response,
            tokens=tokens,
            cost=cost_decimal,
            cassette_hash=sha256_bytes(canonical_json(payload)),
        )

    def verify(self) -> None:
        payload = asdict(self)
        payload.pop("cassette_hash")
        payload["cost"] = str(self.cost)
        if sha256_bytes(canonical_json(payload)) != self.cassette_hash:
            raise CassetteError("hash do cassette não confere")

    def replay(self, request: dict[str, Any]) -> dict[str, Any]:
        self.verify()
        if request != self.request:
            raise CassetteError("request divergente: replay não é permitido")
        return dict(self.response)
