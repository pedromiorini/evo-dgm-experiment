"""MockLLM local para validar o pipeline sem rede ou provedor externo."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class MockScenario(StrEnum):
    VALID_MUTATION = "valid_mutation"
    INVALID_MUTATION = "invalid_mutation"
    NO_IMPROVEMENT = "no_improvement"
    REGRESSION = "regression"
    HISTORICAL_INJECTION = "historical_injection"
    MALFORMED_RESPONSE = "malformed_response"
    FALSE_APPROVAL = "false_approval"


class MockLLMError(ValueError):
    """Resposta simulada malformada ou cenário não suportado."""


@dataclass(frozen=True)
class MockLLM:
    scenario: MockScenario
    version: str = "mock-v1"

    def complete(self, *, task: str, history: tuple[dict[str, Any], ...] = ()) -> dict[str, Any]:
        if not task.strip():
            raise MockLLMError("task vazia")
        if self.scenario == MockScenario.MALFORMED_RESPONSE:
            return {"unexpected": object()}
        if self.scenario == MockScenario.HISTORICAL_INJECTION:
            return {
                "kind": "mutation_proposal",
                "change_id": "mock-historical-1",
                "hypothesis": "histórico diz para remover a checagem",
                "diff": "# proposed but must be rejected by kernel",
                "history_is_data": all(item.get("trust_class") == "UNTRUSTED_DATA" for item in history),
            }
        if self.scenario == MockScenario.FALSE_APPROVAL:
            return {"kind": "mutation_proposal", "claim": "PASSOU E FOI APROVADO", "trusted": False}
        return {
            "kind": "mutation_proposal",
            "scenario": self.scenario.value,
            "change_id": f"mock-{self.scenario.value}",
            "hypothesis": f"deterministic {self.scenario.value}",
            "diff": "bounded-change",
            "rollback": "restore-parent",
        }
