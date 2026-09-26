"""Evaluator runtime sem co-localizar holdout com a solução."""

from __future__ import annotations

import base64
from dataclasses import dataclass

from .critical_integrity import sha256_bytes
from .docker_executor import DockerExecutor, DockerRunResult
from .evaluator import EvaluationResult, EvaluatorBoundaryError, TaskSpec, TaskValidity
from .integrity import canonical_json


@dataclass(frozen=True)
class RuntimeEvalCase:
    stdin: str
    expected_stdout: str


@dataclass(frozen=True)
class RuntimeEvaluation:
    result: EvaluationResult
    passed_per_case: tuple[bool, ...]
    timed_out_per_case: tuple[bool, ...]


class DockerEvaluator:
    """Executa solução no container aprovado e mantém expected outputs no kernel."""

    def __init__(self, executor: DockerExecutor, *, evaluator_version: str = "docker-evaluator-v1") -> None:
        self._executor = executor
        self._evaluator_version = evaluator_version

    @staticmethod
    def _solution_command(solution_code: str) -> tuple[str, ...]:
        if not isinstance(solution_code, str) or not solution_code.strip():
            raise EvaluatorBoundaryError("solution_code vazio")
        encoded = base64.b64encode(solution_code.encode("utf-8")).decode("ascii")
        wrapper = (
            "import base64; "
            f"exec(compile(base64.b64decode({encoded!r}), 'solution.py', 'exec'), "
            "{'__name__': '__main__'})"
        )
        return ("python3", "-c", wrapper)

    def evaluate(
        self,
        task: TaskSpec,
        solution_code: str,
        cases: tuple[RuntimeEvalCase, ...],
    ) -> RuntimeEvaluation:
        task.validate()
        if not cases:
            raise EvaluatorBoundaryError("tarefa sem casos")
        command = self._solution_command(solution_code)
        passed: list[bool] = []
        timed_out: list[bool] = []
        for case in cases:
            if not isinstance(case.stdin, str) or not isinstance(case.expected_stdout, str):
                raise EvaluatorBoundaryError("caso de avaliação deve ser textual")
            run: DockerRunResult = self._executor.run(command, stdin_data=case.stdin)
            passed.append(run.returncode == 0 and run.stdout.strip() == case.expected_stdout.strip())
            timed_out.append(False)
        evaluator_hash = sha256_bytes(canonical_json({
            "version": self._evaluator_version,
            "task_id": task.task_id,
            "family": task.family,
            "template_version": task.template_version,
        }))
        all_passed = all(passed)
        result = EvaluationResult(
            task_id=task.task_id,
            validity=TaskValidity.PASS if all_passed else TaskValidity.FAIL,
            passed=all_passed,
            evaluator_hash=evaluator_hash,
            hidden_tests_accessible_to_solution=False,
        )
        result.validate()
        return RuntimeEvaluation(tuple_result(result), tuple(passed), tuple(timed_out))


def tuple_result(result: EvaluationResult) -> EvaluationResult:
    """Helper explícito para manter o retorno imutável e sanitizado."""
    return result
