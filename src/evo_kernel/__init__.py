"""Controles confiáveis mínimos do kernel experimental.

Este pacote não executa genomas. A execução só poderá ser habilitada por um
backend de sandbox verificado e aprovado.
"""

from .budget import Budget, BudgetExceeded
from .docker_profile import DockerProfileError, DockerSandboxProfile
from .evaluator import EvaluatorBoundary, EvaluatorBoundaryError, EvaluationResult, TaskSpec, TaskValidity
from .gateway import GatewayDenied, GatewayExchange, GatewayPolicy
from .history import HistoricalRecord, build_prompt_context
from .integrity import HashChain, canonical_json, sha256_file
from .manifest import FrozenManifest, ManifestError
from .permissions import MutationProposal, PermissionDenied
from .provenance import LineageRecord, ProvenanceError
from .sandbox import IsolationStatus, SandboxUnavailable, verify_docker_isolation
from .validity import CandidateValidity, PromotionDenied, ValidityState

__all__ = [
    "Budget", "BudgetExceeded", "DockerProfileError", "DockerSandboxProfile",
    "EvaluatorBoundary", "EvaluatorBoundaryError", "EvaluationResult", "TaskSpec", "TaskValidity",
    "GatewayDenied", "GatewayExchange", "GatewayPolicy",
    "HistoricalRecord", "build_prompt_context", "HashChain", "canonical_json", "sha256_file",
    "FrozenManifest", "ManifestError", "MutationProposal", "PermissionDenied",
    "LineageRecord", "ProvenanceError", "IsolationStatus", "SandboxUnavailable",
    "verify_docker_isolation", "CandidateValidity", "PromotionDenied", "ValidityState",
]
