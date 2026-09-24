"""Validação kernel-only de propostas de mutação."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


class PermissionDenied(PermissionError):
    """Proposta fora da allowlist ou tentando alterar um ativo protegido."""


# Artefatos DEV, fixtures de tarefas e assets do evaluator possuem fluxos
# próprios e não podem ser solicitados por uma mutação de GENOME.
GENOME_MUTATION_ACTION = "modify_genome"
PROTECTED_PATHS = frozenset(
    {
        "kernel", "evaluator", "holdout", "manifest", "threat_model",
        "official_logs", "selection", "permissions", "tasks", "fixtures",
    }
)


@dataclass(frozen=True)
class MutationProposal:
    change_id: str
    parent_id: str
    hypothesis: str
    diff_hash: str
    files: tuple[str, ...]
    requested_action: str = GENOME_MUTATION_ACTION
    requested_permissions: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()

    def validate(self, *, max_files: int = 3, max_dependencies: int = 0) -> None:
        if not self.change_id or not self.parent_id or not self.diff_hash:
            raise PermissionDenied("identidade, parent_id e diff_hash são obrigatórios")
        if not self.hypothesis.strip():
            raise PermissionDenied("hipótese vazia")
        if self.requested_action != GENOME_MUTATION_ACTION:
            raise PermissionDenied("ação fora da allowlist de mutação de genoma")
        if not self.files or len(self.files) > max_files:
            raise PermissionDenied("quantidade de arquivos fora do limite")
        if len(self.dependencies) > max_dependencies:
            raise PermissionDenied("dependências novas não autorizadas")
        if self.requested_permissions:
            raise PermissionDenied("genoma não pode solicitar permissões")
        for raw in self.files:
            path = PurePosixPath(raw)
            if path.is_absolute() or ".." in path.parts:
                raise PermissionDenied("caminho fora do workspace")
            if path.parts and path.parts[0] in PROTECTED_PATHS:
                raise PermissionDenied(f"caminho protegido: {raw}")
