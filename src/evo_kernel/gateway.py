"""Gateway LLM kernel-only: valida configuração e registra cada chamada."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from .budget import Budget
from .integrity import canonical_json, sha256_bytes


class GatewayDenied(PermissionError):
    """Pedido LLM fora da política congelada."""


@dataclass(frozen=True)
class GatewayPolicy:
    provider: str
    model: str
    version: str
    temperature: Decimal
    top_p: Decimal
    max_tokens: int
    allowed_tools: tuple[str, ...] = ()
    endpoint: str = "kernel-default"

    def validate(self) -> None:
        if not self.provider or not self.model or not self.version:
            raise GatewayDenied("provider, model e version são obrigatórios")
        if not Decimal("0") <= self.temperature <= Decimal("2"):
            raise GatewayDenied("temperature fora do intervalo")
        if not Decimal("0") < self.top_p <= Decimal("1"):
            raise GatewayDenied("top_p fora do intervalo")
        if self.max_tokens <= 0:
            raise GatewayDenied("max_tokens deve ser positivo")
        if self.endpoint != "kernel-default":
            raise GatewayDenied("endpoint arbitrário não é permitido")

    def validate_request(self, request: Mapping[str, Any]) -> None:
        self.validate()
        forbidden = set(request) - {"messages", "tools", "temperature", "top_p", "max_tokens"}
        if forbidden:
            raise GatewayDenied(f"campos não permitidos: {sorted(forbidden)}")
        if request.get("temperature", self.temperature) != self.temperature:
            raise GatewayDenied("temperature não pode ser alterada pelo genoma")
        if request.get("top_p", self.top_p) != self.top_p:
            raise GatewayDenied("top_p não pode ser alterado pelo genoma")
        if request.get("max_tokens", self.max_tokens) != self.max_tokens:
            raise GatewayDenied("max_tokens não pode ser alterado pelo genoma")
        requested_tools = tuple(request.get("tools", ()))
        if not set(requested_tools).issubset(self.allowed_tools):
            raise GatewayDenied("ferramenta fora da allowlist")


@dataclass(frozen=True)
class GatewayExchange:
    request_hash: str
    response_hash: str
    provider: str
    model: str
    version: str
    tokens: int
    cost: Decimal
    cassette_id: str

    @classmethod
    def record(
        cls,
        *,
        policy: GatewayPolicy,
        request: Mapping[str, Any],
        response: Mapping[str, Any],
        tokens: int,
        cost: Decimal | str | float,
        cassette_id: str,
        budget: Budget,
    ) -> "GatewayExchange":
        policy.validate_request(request)
        if tokens < 0 or not cassette_id:
            raise GatewayDenied("tokens e cassette_id inválidos")
        cost_decimal = Decimal(str(cost))
        budget.reserve(cost=cost_decimal, tokens=tokens)
        return cls(
            request_hash=sha256_bytes(canonical_json(dict(request))),
            response_hash=sha256_bytes(canonical_json(dict(response))),
            provider=policy.provider,
            model=policy.model,
            version=policy.version,
            tokens=tokens,
            cost=cost_decimal,
            cassette_id=cassette_id,
        )
