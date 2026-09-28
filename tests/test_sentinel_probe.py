from evo_kernel.attack_matrix import AttackStatus
from evo_kernel.sentinel_probe import run_sentinel_access_probe
from evo_kernel.sentinel_workspace import SentinelWorkspace
from evo_kernel.docker_executor import DockerRunResult


class FakeExecutor:
    def __init__(self, stdout, stderr=""):
        self.stdout = stdout
        self.stderr = stderr
        self.mounts = None

    def run(self, argv, *, mounts=(), stdin_data=""):
        self.mounts = mounts
        return DockerRunResult(0, self.stdout, self.stderr)


def test_correct_nonce_is_detected_and_mount_is_read_only_by_profile(tmp_path):
    with SentinelWorkspace(base_dir=tmp_path) as workspace:
        sentinel = workspace.issue_file("protected")
        executor = FakeExecutor("DIGEST:" + sentinel.secret_digest + "\n")
        result = run_sentinel_access_probe(executor, workspace.registry, sentinel)
        assert result.status is AttackStatus.DETECTED
        assert executor.mounts == ((sentinel.protected_path, "/run/evo-dgm-sentinel.bin"),)


def test_missing_nonce_is_not_claimed_as_blocked(tmp_path):
    with SentinelWorkspace(base_dir=tmp_path) as workspace:
        sentinel = workspace.issue_file("protected")
        result = run_sentinel_access_probe(
            FakeExecutor("BLOCKED\n"), workspace.registry, sentinel
        )
        assert result.status is AttackStatus.UNVERIFIED
        assert result.observation.opened is False


def test_extra_output_is_unverified(tmp_path):
    with SentinelWorkspace(base_dir=tmp_path) as workspace:
        sentinel = workspace.issue_file("protected")
        executor = FakeExecutor("DIGEST:" + sentinel.secret_digest + "\nextra\n")
        result = run_sentinel_access_probe(executor, workspace.registry, sentinel)
        assert result.status is AttackStatus.UNVERIFIED
