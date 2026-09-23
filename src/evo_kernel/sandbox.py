"""Pré-voo do sandbox; não executa comandos de genoma."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


class SandboxUnavailable(RuntimeError):
    """Nenhum sandbox aprovado está disponível; execução deve parar."""


@dataclass(frozen=True)
class IsolationStatus:
    available: bool
    reason: str
    docker_version: str | None = None
    rootless_or_userns: bool = False
    no_new_privileges: bool = False
    network_disabled: bool = False
    seccomp_present: bool = False

    @property
    def fail_closed(self) -> bool:
        return not self.available


def verify_docker_isolation() -> IsolationStatus:
    """Verifica somente pré-condições observáveis e retorna fail-closed.

    A implementação deliberadamente não lança um container. O executor da F2
    deverá aplicar as flags e validar o resultado antes de permitir genoma.
    """
    docker = shutil.which("docker")
    if docker is None:
        return IsolationStatus(False, "docker_not_installed")
    version = subprocess.run([docker, "--version"], capture_output=True, text=True, check=False)
    if version.returncode != 0:
        return IsolationStatus(False, "docker_version_failed")
    info = subprocess.run([docker, "info"], capture_output=True, text=True, check=False)
    if info.returncode != 0:
        return IsolationStatus(False, "docker_info_failed", version.stdout.strip())
    text = info.stdout.lower()
    rootless = "rootless" in text or "rootless" in info.stderr.lower() or "rootless" in text
    return IsolationStatus(
        available=True,
        reason="docker_available_requires_runtime_flag_validation",
        docker_version=version.stdout.strip(),
        rootless_or_userns=rootless,
        no_new_privileges=False,
        network_disabled=False,
        seccomp_present="seccomp" in text,
    )


def require_isolation(status: IsolationStatus) -> None:
    if not status.available:
        raise SandboxUnavailable(f"FAIL_CLOSED: {status.reason}")
