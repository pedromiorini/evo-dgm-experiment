"""Controles confiáveis mínimos do kernel experimental.

Este pacote não executa genomas. A execução só poderá ser habilitada por um
backend de sandbox verificado e aprovado.
"""

from .budget import Budget, BudgetExceeded
from .history import HistoricalRecord, build_prompt_context
from .integrity import HashChain, canonical_json, sha256_file
from .sandbox import IsolationStatus, SandboxUnavailable, verify_docker_isolation

__all__ = [
    "Budget",
    "BudgetExceeded",
    "HistoricalRecord",
    "build_prompt_context",
    "HashChain",
    "canonical_json",
    "sha256_file",
    "IsolationStatus",
    "SandboxUnavailable",
    "verify_docker_isolation",
]
