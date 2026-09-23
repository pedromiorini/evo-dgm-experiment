"""Validação declarativa de tarefas antes de qualquer análise."""

from __future__ import annotations

from dataclasses import dataclass


class TaskValidationError(ValueError):
    """Tarefa não demonstra discriminação suficiente."""


@dataclass(frozen=True)
class TaskDefinition:
    task_id: str
    family: str
    template_version: str
    domain: str = "programming_io"

    def validate(self) -> None:
        if not all((self.task_id, self.family, self.template_version, self.domain)):
            raise TaskValidationError("definição de tarefa incompleta")


@dataclass(frozen=True)
class TaskValidationResult:
    reference_passes: bool
    null_fails: bool
    adversarial_fails: bool
    metamorphic_discriminates: bool
    hardcoding_checked: bool

    @property
    def valid(self) -> bool:
        return all((
            self.reference_passes,
            self.null_fails,
            self.adversarial_fails,
            self.metamorphic_discriminates,
            self.hardcoding_checked,
        ))

    def require_valid(self) -> None:
        if not self.valid:
            raise TaskValidationError("TASK_VALIDITY=FAIL: discriminação insuficiente")
