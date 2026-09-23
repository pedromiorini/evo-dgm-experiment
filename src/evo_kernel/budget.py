"""Controles de orçamento no domínio confiável."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


class BudgetExceeded(RuntimeError):
    """Operação bloqueada porque excederia o teto congelado."""


@dataclass
class Budget:
    max_total_cost: Decimal
    spent: Decimal = Decimal("0")
    calls: int = 0
    tokens: int = 0

    def __post_init__(self) -> None:
        self.max_total_cost = Decimal(str(self.max_total_cost))
        self.spent = Decimal(str(self.spent))
        if self.max_total_cost < 0 or self.spent < 0 or self.spent > self.max_total_cost:
            raise ValueError("orçamento inválido")

    @property
    def remaining(self) -> Decimal:
        return self.max_total_cost - self.spent

    def reserve(self, *, cost: Decimal | str | float, tokens: int = 0) -> None:
        cost_decimal = Decimal(str(cost))
        if cost_decimal < 0 or tokens < 0:
            raise ValueError("custo e tokens devem ser não negativos")
        if self.spent + cost_decimal > self.max_total_cost:
            raise BudgetExceeded("operação bloqueada: teto de orçamento excedido")
        self.spent += cost_decimal
        self.calls += 1
        self.tokens += tokens
