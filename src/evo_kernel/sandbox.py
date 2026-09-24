"""Pré-voo do sandbox; não executa comandos de genoma.

Docker instalado é apenas uma pré-condição. Sem verificação efetiva do
container que será usado, a autorização permanece FAIL_CLOSED.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class SandboxUnavailable(RuntimeError):
    """Nenhum sandbox aprovado está disponível; execução deve parar."""


class SandboxEnvError(PermissionError):
    """Ambiente ou caminho fora da política mínima."""


_MINIMAL_ENV_ALLOWLIST = frozenset({"PATH", "LANG", "LC_ALL", "PYTHONHASHSEED"})


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
    """Aprova somente perfil efetivamente aplicado e verificável."""
    docker = shutil.which("docker")
    if docker is None:
        return IsolationStatus(False, "docker_not_installed")
    version = subprocess.run([docker, "--version"], capture_output=True, text=True, check=False)
    if version.returncode != 0:
        return IsolationStatus(False, "docker_version_failed")
    info = subprocess.run([docker, "info"], capture_output=True, text=True, check=False)
    if info.returncode != 0:
        return IsolationStatus(False, "docker_info_failed", version.stdout.strip())
    return IsolationStatus(False, "docker_present_runtime_profile_unverified", version.stdout.strip())


def require_isolation(status: IsolationStatus) -> None:
    if not status.available or not status.all_required_properties_verified:
        raise SandboxUnavailable(f"FAIL_CLOSED: {status.reason}")


def build_minimal_env(*, extra_env: dict[str, str] | None = None) -> dict[str, str]:
    """Monta ambiente mínimo; variáveis adicionais são rejeitadas por padrão."""
    env = {key: os.environ[key] for key in _MINIMAL_ENV_ALLOWLIST if key in os.environ}
    if extra_env:
        forbidden = set(extra_env) - _MINIMAL_ENV_ALLOWLIST
        if forbidden:
            raise SandboxEnvError(f"variáveis fora da allowlist: {sorted(forbidden)}")
        env.update(extra_env)
    return env


def _safe_relative_path(raw_path: str) -> Path:
    if not raw_path or "\\" in raw_path:
        raise SandboxEnvError("caminho vazio ou separador inválido")
    pure = PurePosixPath(raw_path)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise SandboxEnvError(f"caminho não relativo seguro: {raw_path!r}")
    return Path(*pure.parts)


def make_isolated_workdir(*, allowed_files: dict[str, str], base_tmp: Path | None = None) -> Path:
    """Cria workdir descartável e rejeita escapes de path antes da escrita."""
    workdir = Path(tempfile.mkdtemp(prefix="evo_dgm_sandbox_", dir=base_tmp))
    root = workdir.resolve()
    for raw_path, content in allowed_files.items():
        relative = _safe_relative_path(raw_path)
        target = (root / relative).resolve()
        if root not in target.parents:
            raise SandboxEnvError(f"path escapa do workdir: {raw_path!r}")
        if not isinstance(content, str):
            raise SandboxEnvError("conteúdo deve ser texto")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return workdir
