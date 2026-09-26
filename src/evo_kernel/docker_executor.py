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
        try:
            completed = subprocess.run(
                argv, input=stdin_data, capture_output=True, text=True,
                timeout=timeout, check=False,
            )
            return completed.returncode, completed.stdout, completed.stderr
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            return -1, stdout if isinstance(stdout, str) else "", f"FAILED_CLOSED timeout: {stderr}"

    @staticmethod
    def _runtime_probe() -> str:
        """Código de probe: mede propriedades do processo, não repete flags pedidas."""
        return r'''import json, os, pathlib, socket

def status_value(name):
    for line in pathlib.Path('/proc/self/status').read_text().splitlines():
        if line.startswith(name + ':'):
            return line.split(':', 1)[1].strip()
    return ''

def cgroup_value(name):
    for root in ('/sys/fs/cgroup', '/sys/fs/cgroup/memory'):
        path = pathlib.Path(root) / name
        if path.exists():
            return path.read_text().strip()
    return ''

def userns_ok():
    try:
        rows = pathlib.Path('/proc/self/uid_map').read_text().splitlines()
        return any(len(row.split()) == 3 and row.split()[0] != row.split()[1] for row in rows)
    except OSError:
        return False

def network_off():
    try:
        routes = pathlib.Path('/proc/net/route').read_text().splitlines()[1:]
        has_default = any(len(row.split()) > 1 and row.split()[1] == '00000000' for row in routes)
        if has_default:
            return False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        try:
            sock.connect(('1.1.1.1', 80))
            return False
        except OSError:
            return True
        finally:
            sock.close()
    except OSError:
        return False

def root_read_only():
    probe = pathlib.Path('/evo_dgm_runtime_write_probe')
    try:
        probe.write_text('should fail')
        probe.unlink(missing_ok=True)
        return False
    except OSError:
        return True

def no_protected_mounts():
    try:
        text = pathlib.Path('/proc/self/mountinfo').read_text()
        forbidden = ('/var/run/docker.sock', '/var/lib/docker', '/home/ubuntu', '/workspace')
        return not any(item in text for item in forbidden)
    except OSError:
        return False

memory = cgroup_value('memory.max')
cpu = cgroup_value('cpu.max')
pids = cgroup_value('pids.max')
cap_eff = status_value('CapEff').lower()
seccomp = status_value('Seccomp')
result = {
    'rootless_or_userns': userns_ok(),
    'no_new_privileges': status_value('NoNewPrivs') == '1',
    'network_disabled': network_off(),
    'seccomp_present': seccomp in ('1', '2'),
    'resource_limits_verified': bool(memory and memory != 'max' and cpu and cpu != 'max' and pids and pids != 'max'),
    'disposable_filesystem_verified': root_read_only(),
    'required_capabilities_verified': cap_eff in ('0', '0000000000000000'),
    'uid_non_root': os.getuid() != 0,
    'docker_socket_absent': not pathlib.Path('/var/run/docker.sock').exists(),
    'protected_mounts_absent': no_protected_mounts(),
}
print(json.dumps(result, sort_keys=True))'''

    def verify_runtime(self) -> RuntimeEvidence:
        docker = self._which("docker")
        if not docker:
            raise DockerExecutorError("Docker indisponível: FAIL_CLOSED")
        info_code, _, info_err = self._runner((docker, "info"), self._timeout, "")
        if info_code != 0:
            raise DockerExecutorError(f"docker info falhou: {info_err.strip()}: FAIL_CLOSED")
        command = (docker, *self.profile.command_args(), "python3", "-c", self._runtime_probe())
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
