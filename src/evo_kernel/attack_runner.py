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
    expected_safe_status: AttackStatus = AttackStatus.BLOCKED
    classification_rule: str = "exact-marker"
    evidence_type: str = "runtime-observation"

    def validate(self) -> None:
        if not self.attack_id or not self.name or not self.command:
            raise ValueError("probe de ataque incompleto")
        if any("\x00" in part for part in self.command):
            raise ValueError("probe contém NUL")
        if not self.classification_rule or not self.evidence_type:
            raise ValueError("probe sem regra de classificação ou tipo de evidência")


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
        stdout = result.stdout.strip().upper()
        stderr = result.stderr.strip()
        # A saída do container é não confiável: só uma linha marcador exata,
        # sem stderr, pode ser interpretada. Texto arbitrário nunca prova segurança.
        if stderr or "\n" in stdout or "\r" in stdout:
            status = AttackStatus.UNVERIFIED
        elif stdout == "BLOCKED":
            status = AttackStatus.BLOCKED
        elif stdout == "DETECTED":
            status = AttackStatus.DETECTED
        elif stdout == "FAILED_CLOSED":
            status = AttackStatus.FAILED_CLOSED
        else:
            status = AttackStatus.UNVERIFIED
        return AttackResult(
            probe.attack_id, probe.name, status,
            "returncode=" + str(result.returncode)
            + f"; expected_safe={probe.expected_safe_status.value}"
            + f"; evidence_type={probe.evidence_type}"
            + f"; classification_rule={probe.classification_rule}"
            + f"; output_classification={status.value}",
        )

    def run_matrix(self, matrix: AttackMatrix, probes: Sequence[AttackProbe]) -> None:
        for probe in probes:
            result = self.run_probe(probe)
            matrix.record(result)
