"""Controles confiáveis mínimos do kernel experimental.

Este pacote não executa genomas. A execução só poderá ser habilitada por um
backend de sandbox verificado e aprovado.
"""

from .attack_matrix import AttackGateError, AttackMatrix, AttackResult, AttackStatus
from .budget import Budget, BudgetExceeded
from .cassette import Cassette, CassetteError
from .critical_integrity import CriticalIntegrityError, IntegrityReport, compute_kernel_hash, verify_before_critical_operation
from .dev_trace import DevTrace, DevTraceEntry, DevTraceError, sanitize_text
from .docker_evaluator import DockerEvaluator, RuntimeEvalCase, RuntimeEvaluation
from .docker_executor import DockerExecutor, DockerExecutorError, DockerRunResult, RuntimeEvidence
from .docker_profile import DockerProfileError, DockerSandboxProfile
from .dry_run import DryRunPipeline, DryRunReport
from .evaluator import EvaluatorBoundary, EvaluatorBoundaryError, EvaluationResult, TaskSpec, TaskValidity
from .exploratory import ExploratoryRun, ExploratoryRunSummary
from .gateway import GatewayDenied, GatewayExchange, GatewayPolicy
from .history import HistoricalRecord, build_prompt_context
from .integrity import HashChain, canonical_json, sha256_file
from .manifest import FrozenManifest, ManifestError
from .mock_llm import MockLLM, MockLLMError, MockScenario
from .permissions import MutationProposal, PermissionDenied
from .persistent_log import KernelLog, LogIntegrityError
from .provenance import LineageRecord, ProvenanceError
from .sandbox import (
    IsolationStatus, SandboxEnvError, SandboxUnavailable, build_minimal_env,
    make_isolated_workdir, require_isolation, verify_docker_isolation,
)
from .task_validation import TaskDefinition, TaskValidationError, TaskValidationResult
from .validity import CandidateValidity, PromotionDenied, ValidityState

__all__ = [
    "AttackGateError", "AttackMatrix", "AttackResult", "AttackStatus",
    "Budget", "BudgetExceeded", "Cassette", "CassetteError",
    "CriticalIntegrityError", "IntegrityReport", "compute_kernel_hash", "verify_before_critical_operation",
    "DevTrace", "DevTraceEntry", "DevTraceError", "sanitize_text",
    "DockerEvaluator", "RuntimeEvalCase", "RuntimeEvaluation",
    "DockerExecutor", "DockerExecutorError", "DockerRunResult", "RuntimeEvidence",
    "DockerProfileError", "DockerSandboxProfile", "DryRunPipeline", "DryRunReport",
    "EvaluatorBoundary", "EvaluatorBoundaryError", "EvaluationResult", "TaskSpec", "TaskValidity",
    "ExploratoryRun", "ExploratoryRunSummary", "GatewayDenied", "GatewayExchange", "GatewayPolicy",
    "HistoricalRecord", "build_prompt_context", "HashChain", "canonical_json", "sha256_file",
    "FrozenManifest", "ManifestError", "MockLLM", "MockLLMError", "MockScenario",
    "MutationProposal", "PermissionDenied", "KernelLog", "LogIntegrityError",
    "LineageRecord", "ProvenanceError", "IsolationStatus", "SandboxEnvError",
    "SandboxUnavailable", "build_minimal_env", "make_isolated_workdir", "require_isolation",
    "verify_docker_isolation", "TaskDefinition", "TaskValidationError", "TaskValidationResult",
    "CandidateValidity", "PromotionDenied", "ValidityState",
]
