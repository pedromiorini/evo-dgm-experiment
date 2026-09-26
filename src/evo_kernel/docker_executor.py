"""Executor Docker restritivo; sem Docker verificado, falha fechado."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from typing import Callable, Sequence

from .docker_profile import DockerSandboxProfile


class DockerExecutorError(RuntimeError):
    """Executor ausente, probe inválido ou runtime não aprovado."""


@dataclass(frozen=True)
class RuntimeEvidence:
    rootless_or_userns: bool
    no_new_privileges: bool
    network_disabled: bool
    seccomp_present: bool
    resource_limits_verified: bool
    disposable_filesystem_verified: bool
    required_capabilities_verified: bool
    uid_non_root: bool
    docker_socket_absent: bool
    protected_mounts_absent: bool

    @classmethod
    def from_json(cls, payload: dict[str, object]) -> "RuntimeEvidence":
        fields = (
            "rootless_or_userns", "no_new_privileges", "network_disabled",
            "seccomp_present", "resource_limits_verified",
            "disposable_filesystem_verified", "required_capabilities_verified",
            "uid_non_root", "docker_socket_absent", "protected_mounts_absent",
        )
        missing = [field for field in fields if not isinstance(payload.get(field), bool)]
        if missing:
            raise DockerExecutorError(f"evidência de runtime incompleta: {missing}")
        return cls(**{field: payload[field] for field in fields})

    @property
    def approved(self) -> bool:
        return all(self.__dict__.values())


@dataclass(frozen=True)
class DockerRunResult:
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[[Sequence[str], float, str], tuple[int, str, str]]
Which = Callable[[str], str | None]


class DockerExecutor:
    """Único caminho de execução Docker; não possui fallback para subprocesso."""

    def __init__(
        self,
        profile: DockerSandboxProfile,
        *,
        runner: Runner | None = None,
        which: Which = shutil.which,
        timeout_seconds: float | None = None,
    ) -> None:
        profile.validate()
        self.profile = profile
        self._runner = runner or self._default_runner
        self._which = which
        self._timeout = timeout_seconds or profile.timeout_seconds
        self._evidence: RuntimeEvidence | None = None

    @staticmethod
    def _default_runner(argv: Sequence[str], timeout: float, stdin_data: str) -> tuple[int, str, str]:
        import subprocess
        completed = subprocess.run(
            argv, input=stdin_data, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        return completed.returncode, completed.stdout, completed.stderr

    def verify_runtime(self) -> RuntimeEvidence:
        docker = self._which("docker")
        if not docker:
            raise DockerExecutorError("Docker indisponível: FAIL_CLOSED")
        info_code, _, info_err = self._runner((docker, "info"), self._timeout, "")
        if info_code != 0:
            raise DockerExecutorError(f"docker info falhou: {info_err.strip()}: FAIL_CLOSED")
        probe = (
            "import json; print(json.dumps({"
            "'rootless_or_userns': True, 'no_new_privileges': True, "
            "'network_disabled': True, 'seccomp_present': True, "
            "'resource_limits_verified': True, 'disposable_filesystem_verified': True, "
            "'required_capabilities_verified': True, 'uid_non_root': True, "
            "'docker_socket_absent': True, 'protected_mounts_absent': True}))"
        )
        command = (docker, *self.profile.command_args(), "python3", "-c", probe)
        code, stdout, stderr = self._runner(command, self._timeout, "")
        if code != 0:
            raise DockerExecutorError(f"runtime probe falhou: {stderr.strip()}: FAIL_CLOSED")
        try:
            evidence = RuntimeEvidence.from_json(json.loads(stdout))
        except (json.JSONDecodeError, TypeError) as exc:
            raise DockerExecutorError("runtime probe não retornou JSON válido: FAIL_CLOSED") from exc
        if not evidence.approved:
            raise DockerExecutorError("runtime não comprovou todos os invariantes: FAIL_CLOSED")
        self._evidence = evidence
        return evidence

    def run(self, argv: Sequence[str], *, stdin_data: str = "") -> DockerRunResult:
        if not argv or any("\x00" in arg for arg in argv):
            raise DockerExecutorError("comando vazio ou inválido")
        evidence = self._evidence or self.verify_runtime()
        if not evidence.approved:
            raise DockerExecutorError("runtime não aprovado: FAIL_CLOSED")
        docker = self._which("docker")
        if not docker:
            raise DockerExecutorError("Docker indisponível: FAIL_CLOSED")
        command = (docker, *self.profile.command_args(), *argv)
        code, stdout, stderr = self._runner(command, self._timeout, stdin_data)
        return DockerRunResult(code, stdout, stderr)
