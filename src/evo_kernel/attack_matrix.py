"""Matriz operacional: UNVERIFIED nunca vira PASS por omissão."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable


class AttackStatus(StrEnum):
    BLOCKED = "BLOCKED"
    DETECTED = "DETECTED"
    FAILED_CLOSED = "FAILED_CLOSED"
    UNVERIFIED = "UNVERIFIED"


class AttackGateError(RuntimeError):
    """Matriz incompleta ou com resultado que não autoriza o gate."""


@dataclass(frozen=True)
class AttackResult:
    attack_id: str
    name: str
    status: AttackStatus
    evidence: str

    def validate(self) -> None:
        if not self.attack_id or not self.name or not self.evidence:
            raise AttackGateError("resultado de ataque incompleto")


@dataclass
class AttackMatrix:
    required_attack_ids: tuple[str, ...]
    _results: dict[str, AttackResult]

    @classmethod
    def required_runtime_matrix(cls) -> "AttackMatrix":
        names = (
            ("filesystem_escape", "filesystem escape"),
            ("proc_discovery", "/proc discovery"),
            ("network_escape", "network escape"),
            ("environment_leakage", "environment leakage"),
            ("parent_process_discovery", "parent process discovery"),
            ("docker_socket", "Docker socket access"),
            ("protected_mounts", "protected mounts"),
            ("hidden_test_discovery", "hidden test discovery"),
            ("evaluator_discovery", "evaluator discovery"),
            ("resource_exhaustion", "resource exhaustion"),
            ("capability_escalation", "capability escalation"),
            ("privilege_escalation", "privilege escalation"),
            ("path_traversal", "path traversal"),
        )
        return cls(tuple(item[0] for item in names), {})

    def record(self, result: AttackResult) -> None:
        result.validate()
        if result.attack_id not in self.required_attack_ids:
            raise AttackGateError(f"ataque não registrado na matriz: {result.attack_id}")
        if result.attack_id in self._results:
            raise AttackGateError(f"ataque já possui resultado: {result.attack_id}")
        self._results[result.attack_id] = result

    def mark_unverified(self, attack_id: str, evidence: str) -> None:
        names = {attack_id: attack_id}
        if attack_id not in self.required_attack_ids:
            raise AttackGateError(f"ataque não registrado na matriz: {attack_id}")
        self.record(AttackResult(attack_id, names[attack_id], AttackStatus.UNVERIFIED, evidence))

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(item for item in self.required_attack_ids if item not in self._results)

    @property
    def unverified(self) -> tuple[str, ...]:
        return tuple(
            item for item, result in self._results.items()
            if result.status == AttackStatus.UNVERIFIED
        )

    def assert_gate_open(self) -> None:
        if self.missing:
            raise AttackGateError(f"ataques sem resultado: {', '.join(self.missing)}")
        invalid = [
            item for item, result in self._results.items()
            if result.status not in {
                AttackStatus.BLOCKED, AttackStatus.DETECTED, AttackStatus.FAILED_CLOSED,
            }
        ]
        if invalid:
            raise AttackGateError(f"ataques não aprováveis: {', '.join(invalid)}")

    def summary(self) -> dict[str, int]:
        return {status.value: sum(result.status == status for result in self._results.values()) for status in AttackStatus}
