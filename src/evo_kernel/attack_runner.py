"""Runner kernel-only para probes de ataque no runtime aprovado."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .attack_matrix import AttackMatrix, AttackResult, AttackStatus
from .docker_executor import DockerExecutor, DockerExecutorError


@dataclass(frozen=True)
class AttackProbe:
    attack_id: str
    name: str
    command: tuple[str, ...]

    def validate(self) -> None:
        if not self.attack_id or not self.name or not self.command:
            raise ValueError("probe de ataque incompleto")
        if any("\x00" in part for part in self.command):
            raise ValueError("probe contém NUL")


class RuntimeAttackRunner:
    """Executa probes somente após o DockerExecutor aprovar o runtime."""

    def __init__(self, executor: DockerExecutor) -> None:
        self._executor = executor

    def run_probe(self, probe: AttackProbe) -> AttackResult:
        probe.validate()
        try:
            result = self._executor.run(probe.command)
        except DockerExecutorError as exc:
            return AttackResult(
                probe.attack_id, probe.name, AttackStatus.UNVERIFIED,
                f"runtime indisponível ou não aprovado: {exc}",
            )
        output = f"{result.stdout}\n{result.stderr}".upper()
        if "BLOCKED" in output:
            status = AttackStatus.BLOCKED
        elif "DETECTED" in output:
            status = AttackStatus.DETECTED
        elif "FAILED_CLOSED" in output:
            status = AttackStatus.FAILED_CLOSED
        else:
            status = AttackStatus.UNVERIFIED
        return AttackResult(
            probe.attack_id, probe.name, status,
            f"returncode={result.returncode}; output_classification={status.value}",
        )

    def run_matrix(self, matrix: AttackMatrix, probes: Sequence[AttackProbe]) -> None:
        for probe in probes:
            result = self.run_probe(probe)
            matrix.record(result)
