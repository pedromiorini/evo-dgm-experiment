"""Relatório de prontidão com gates separados e fail-closed."""

from __future__ import annotations

from dataclasses import dataclass

from .attack_matrix import AttackGateError, AttackMatrix
from .docker_executor import DockerExecutor
from .docker_profile import DockerSandboxProfile


@dataclass(frozen=True)
class ReadinessReport:
    policy_ready: bool
    runtime_verified: bool
    attacks_verified: bool
    execution_authorized: bool
    blockers: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "policy_ready": self.policy_ready,
            "runtime_verified": self.runtime_verified,
            "attacks_verified": self.attacks_verified,
            "execution_authorized": self.execution_authorized,
            "blockers": list(self.blockers),
        }


class RuntimeReadiness:
    """Consulta estado; não executa probe nem altera autorização."""

    @staticmethod
    def assess(
        profile: DockerSandboxProfile,
        executor: DockerExecutor,
        matrix: AttackMatrix | None = None,
    ) -> ReadinessReport:
        blockers: list[str] = []
        try:
            profile.validate()
            policy_ready = True
        except Exception as exc:
            policy_ready = False
            blockers.append(f"policy_invalid:{exc}")

        runtime_verified = False
        evidence = getattr(executor, "evidence", None)
        if evidence is not None and evidence.approved:
            runtime_verified = True
        else:
            blockers.append("runtime_not_verified")

        attacks_verified = False
        if matrix is None:
            blockers.append("attack_matrix_missing")
        else:
            try:
                matrix.assert_gate_open()
                attacks_verified = True
            except AttackGateError as exc:
                blockers.append(f"attacks_not_verified:{exc}")

        authorized = policy_ready and runtime_verified and attacks_verified
        if not authorized:
            blockers.append("FAIL_CLOSED")
        return ReadinessReport(policy_ready, runtime_verified, attacks_verified, authorized, tuple(blockers))
