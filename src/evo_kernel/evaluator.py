"""Contrato kernel-only para evitar co-localização entre solução e evaluator."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class EvaluatorBoundaryError(PermissionError):
    """Layout ou resultado viola a separação solution/evaluator."""


class TaskValidity(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    family: str
    template_version: str
    hidden_test_set_id: str

    def validate(self) -> None:
        if not all((self.task_id, self.family, self.template_version, self.hidden_test_set_id)):
            raise EvaluatorBoundaryError("TaskSpec incompleta")


@dataclass(frozen=True)
class EvaluationResult:
    task_id: str
    validity: TaskValidity
    passed: bool
    evaluator_hash: str
    hidden_tests_accessible_to_solution: bool = False

    def validate(self) -> None:
        if self.hidden_tests_accessible_to_solution:
            raise EvaluatorBoundaryError("holdout acessível à solução")
        if not self.evaluator_hash:
            raise EvaluatorBoundaryError("evaluator_hash obrigatório")
        if self.validity == TaskValidity.PASS and not self.passed:
            raise EvaluatorBoundaryError("resultado PASS inconsistente")


@dataclass(frozen=True)
class EvaluatorBoundary:
    solution_root: Path
    evaluator_root: Path
    holdout_root: Path

    def validate_separation(self) -> None:
        roots = [p.resolve() for p in (self.solution_root, self.evaluator_root, self.holdout_root)]
        if len(set(roots)) != 3:
            raise EvaluatorBoundaryError("solution, evaluator e holdout não podem compartilhar raiz")
        for index, root in enumerate(roots):
            for other in roots[index + 1 :]:
                if root in other.parents or other in root.parents:
                    raise EvaluatorBoundaryError("roots de confiança estão aninhadas")

    def build_transport_contract(self) -> dict[str, str]:
        self.validate_separation()
        return {
            "solution_to_kernel": "stdin/stdout-or-rpc",
            "kernel_to_evaluator": "structured-task-id-and-output",
            "holdout_to_solution": "forbidden",
            "evaluator_to_solution": "sanitized-result-only",
        }
