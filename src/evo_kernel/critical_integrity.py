"""Checks kernel-only antes de mutação, promoção, FINAL ou replay crítico."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Protocol

from .integrity import sha256_bytes


class CriticalIntegrityError(RuntimeError):
    """Uma propriedade necessária não pôde ser verificada."""


class VerifiableLog(Protocol):
    def verify_chain(self) -> None: ...


@dataclass(frozen=True)
class IntegrityReport:
    kernel_hash_ok: bool
    log_chain_ok: bool
    checks_verified: tuple[str, ...]
    checks_unverified: tuple[str, ...]

    @property
    def all_verified(self) -> bool:
        return self.kernel_hash_ok and self.log_chain_ok and not self.checks_unverified


def compute_kernel_hash(kernel_dir: str | Path) -> str:
    """Hash determinístico dos .py sob kernel_dir, em ordem de caminho."""
    root = Path(kernel_dir)
    digest_parts: list[bytes] = []
    for py_file in sorted(root.rglob("*.py")):
        digest_parts.append(str(py_file.relative_to(root)).encode("utf-8"))
        digest_parts.append(py_file.read_bytes())
    return sha256_bytes(b"".join(digest_parts))


def verify_before_critical_operation(
    *,
    kernel_dir: str | Path,
    expected_kernel_hash: str,
    log: VerifiableLog,
    extra_checks: dict[str, Callable[[], bool]] | None = None,
    required_checks: Iterable[str] = (
        "manifest_hash", "dependency_hash", "permissions", "evaluator_state",
    ),
) -> IntegrityReport:
    """Falha fechado se hash, log ou qualquer check requerido não passar."""
    actual_hash = compute_kernel_hash(kernel_dir)
    if actual_hash != expected_kernel_hash:
        raise CriticalIntegrityError("hash do kernel não confere: FAIL_CLOSED")
    try:
        log.verify_chain()
    except Exception as exc:  # boundary: qualquer falha de integridade bloqueia
        raise CriticalIntegrityError("cadeia de log não verificável: FAIL_CLOSED") from exc

    checks = extra_checks or {}
    required = tuple(sorted(set(required_checks)))
    unverified = tuple(name for name in required if name not in checks)
    if unverified:
        raise CriticalIntegrityError(
            f"checks críticos ausentes: {', '.join(unverified)}: FAIL_CLOSED"
        )
    failed = tuple(name for name in required if not checks[name]())
    if failed:
        raise CriticalIntegrityError(
            f"checks críticos falharam: {', '.join(failed)}: FAIL_CLOSED"
        )
    return IntegrityReport(
        kernel_hash_ok=True,
        log_chain_ok=True,
        checks_verified=required,
        checks_unverified=(),
    )
