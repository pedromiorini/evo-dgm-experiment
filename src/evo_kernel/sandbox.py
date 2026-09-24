"""Pré-voo do sandbox; não executa comandos de genoma.

Docker instalado é apenas uma pré-condição. Sem verificação efetiva do
container que será usado, a autorização permanece FAIL_CLOSED.
"""

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
    resource_limits_verified: bool = False
    disposable_filesystem_verified: bool = False
    required_capabilities_verified: bool = False

    @property
    def fail_closed(self) -> bool:
        return not self.available

    @property
    def all_required_properties_verified(self) -> bool:
        return all((
            self.rootless_or_userns,
            self.no_new_privileges,
            self.network_disabled,
            self.seccomp_present,
            self.resource_limits_verified,
            self.disposable_filesystem_verified,
            self.required_capabilities_verified,
        ))


def verify_docker_isolation() -> IsolationStatus:
    """Verifica disponibilidade, mas aprova somente um perfil efetivamente verificado.

    Este módulo ainda não possui executor de container. Portanto, mesmo quando
    ``docker info`` funciona, as propriedades aplicadas ao container não são
    comprovadas e ``available`` permanece falso. Isso é intencional e evita
    transformar suporte do runtime em evidência de isolamento.
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
    return IsolationStatus(
        available=False,
        reason="docker_present_runtime_profile_unverified",
        docker_version=version.stdout.strip(),
    )


def require_isolation(status: IsolationStatus) -> None:
    if not status.available or not status.all_required_properties_verified:
        raise SandboxUnavailable(f"FAIL_CLOSED: {status.reason}")
