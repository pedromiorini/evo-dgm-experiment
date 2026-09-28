"""Perfil declarativo de Docker para revisão; não invoca o Docker CLI."""

from __future__ import annotations

from dataclasses import dataclass


class DockerProfileError(ValueError):
    """Perfil não satisfaz os invariantes mínimos da SPEC."""


@dataclass(frozen=True)
class DockerSandboxProfile:
    image: str
    memory: str = "512m"
    cpus: str = "1.0"
    pids_limit: int = 128
    timeout_seconds: int = 30
    network: str = "none"
    read_only: bool = True
    no_new_privileges: bool = True
    drop_all_capabilities: bool = True
    user: str = "65532:65532"

    def validate(self) -> None:
        if not self.image or "@sha256:" not in self.image or self.network != "none":
            raise DockerProfileError("imagem deve ser fixada por digest e rede negada é obrigatória")
        if not self.read_only or not self.no_new_privileges or not self.drop_all_capabilities:
            raise DockerProfileError("perfil não atende filesystem read-only/no-new-privileges/cap-drop")
        if self.pids_limit <= 0 or self.timeout_seconds <= 0:
            raise DockerProfileError("limites de processos e tempo devem ser positivos")

    def command_args(self, *, mounts: tuple[tuple[str, str], ...] = ()) -> tuple[str, ...]:
        self.validate()
        mount_args: list[str] = []
        for source, destination in mounts:
            if not source.startswith("/") or not destination.startswith("/"):
                raise DockerProfileError("mount de sentinel deve usar paths absolutos")
            mount_args.extend(("--mount", f"type=bind,src={source},dst={destination},readonly"))
        return (
            "run", "--rm", "--pull=never", "--interactive", "--network=none", "--read-only",
            "--security-opt=no-new-privileges", "--cap-drop=ALL",
            f"--memory={self.memory}", f"--cpus={self.cpus}",
            f"--pids-limit={self.pids_limit}", f"--user={self.user}", *mount_args, self.image,
        )
