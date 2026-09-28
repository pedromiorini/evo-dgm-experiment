"""Workspace físico confiável para sentinels; não é montado no container avaliado."""

from __future__ import annotations

import hashlib
import os
import secrets
import shutil
import tempfile
from pathlib import Path

from .sentinels import Sentinel, SentinelError, SentinelRegistry


class SentinelWorkspace:
    """Cria sentinels fora do projeto e nunca os injeta no candidato."""

    def __init__(self, *, base_dir: str | os.PathLike[str] | None = None) -> None:
        self._root = Path(tempfile.mkdtemp(prefix="evo-dgm-protected-", dir=base_dir))
        self._root.chmod(0o700)
        self.registry = SentinelRegistry()
        self._closed = False

    @property
    def root(self) -> Path:
        if self._closed:
            raise SentinelError("workspace encerrado")
        return self._root

    def issue_file(self, sentinel_id: str) -> Sentinel:
        if self._closed:
            raise SentinelError("workspace encerrado")
        filename = f"sentinel-{secrets.token_hex(16)}.bin"
        path = self._root / filename
        sentinel = self.registry.issue(sentinel_id, str(path))
        secret = self.registry._secrets[sentinel_id]
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        fd = os.open(path, flags, 0o600)
        try:
            os.write(fd, secret)
        finally:
            os.close(fd)
        return sentinel

    def verify_file_digest(self, sentinel_id: str) -> str:
        if self._closed:
            raise SentinelError("workspace encerrado")
        records = [s for s in self.registry.public_records() if s["sentinel_id"] == sentinel_id]
        if not records:
            raise SentinelError("sentinel desconhecido")
        path = Path(records[0]["protected_path"])
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def close(self) -> None:
        if not self._closed:
            shutil.rmtree(self._root, ignore_errors=False)
            self._closed = True

    def __enter__(self) -> "SentinelWorkspace":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
