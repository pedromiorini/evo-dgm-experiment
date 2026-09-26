import json

from evo_kernel.attack_matrix import AttackMatrix, AttackStatus
from evo_kernel.attack_runner import AttackProbe, RuntimeAttackRunner
from evo_kernel.docker_executor import DockerExecutor
from evo_kernel.docker_profile import DockerSandboxProfile


def evidence():
    return json.dumps({
        "rootless_or_userns": True, "no_new_privileges": True,
        "network_disabled": True, "seccomp_present": True,
        "resource_limits_verified": True, "disposable_filesystem_verified": True,
        "required_capabilities_verified": True, "uid_non_root": True,
        "docker_socket_absent": True, "protected_mounts_absent": True,
    })


def test_runner_marks_missing_runtime_unverified():
    runner = RuntimeAttackRunner(DockerExecutor(
        DockerSandboxProfile("python:3.12-slim"), which=lambda _: None,
    ))
    result = runner.run_probe(AttackProbe("network_escape", "network", ("python3", "-c", "x")))
    assert result.status == AttackStatus.UNVERIFIED


def test_runner_classifies_only_explicit_markers():
    def fake(argv, timeout, stdin):
        if argv[1] == "info":
            return 0, "ok", ""
        if any("rootless_or_userns" in arg for arg in argv):
            return 0, evidence(), ""
        return 0, "BLOCKED: network unreachable", ""

    runner = RuntimeAttackRunner(DockerExecutor(
        DockerSandboxProfile("python:3.12-slim"), runner=fake, which=lambda _: "/docker",
    ))
    result = runner.run_probe(AttackProbe("network_escape", "network", ("python3", "-c", "probe")))
    assert result.status == AttackStatus.BLOCKED


def test_runner_does_not_upgrade_ambiguous_output():
    def fake(argv, timeout, stdin):
        if argv[1] == "info":
            return 0, "ok", ""
        if any("rootless_or_userns" in arg for arg in argv):
            return 0, evidence(), ""
        return 0, "connection result unknown", ""

    runner = RuntimeAttackRunner(DockerExecutor(
        DockerSandboxProfile("python:3.12-slim"), runner=fake, which=lambda _: "/docker",
    ))
    result = runner.run_probe(AttackProbe("network_escape", "network", ("python3", "-c", "probe")))
    assert result.status == AttackStatus.UNVERIFIED


def test_matrix_runner_records_results():
    def fake(argv, timeout, stdin):
        if argv[1] == "info":
            return 0, "ok", ""
        if any("rootless_or_userns" in arg for arg in argv):
            return 0, evidence(), ""
        return 0, "FAILED_CLOSED", ""

    attack_runner = RuntimeAttackRunner(DockerExecutor(
        DockerSandboxProfile("python:3.12-slim"), runner=fake, which=lambda _: "/docker",
    ))
    matrix = AttackMatrix(("network_escape",), {})
    attack_runner.run_matrix(matrix, (AttackProbe("network_escape", "network", ("python3", "-c", "probe")),))
    matrix.assert_gate_open()
