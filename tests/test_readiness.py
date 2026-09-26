import json

from evo_kernel.attack_matrix import AttackMatrix, AttackResult, AttackStatus
from evo_kernel.docker_executor import DockerExecutor
from evo_kernel.docker_profile import DockerSandboxProfile
from evo_kernel.readiness import RuntimeReadiness


def test_readiness_is_blocked_without_runtime_and_attacks():
    profile = DockerSandboxProfile("python:3.12-slim")
    executor = DockerExecutor(profile, which=lambda _: None)
    report = RuntimeReadiness.assess(profile, executor, AttackMatrix(("a",), {}))
    assert report.policy_ready
    assert not report.runtime_verified
    assert not report.attacks_verified
    assert not report.execution_authorized
    assert "FAIL_CLOSED" in report.blockers


def test_readiness_requires_complete_attack_matrix_even_with_mocked_evidence():
    def fake(argv, timeout, stdin):
        if argv[1] == "info":
            return 0, "ok", ""
        if any("rootless_or_userns" in arg for arg in argv):
            return 0, json.dumps({
                "rootless_or_userns": True, "no_new_privileges": True,
                "network_disabled": True, "seccomp_present": True,
                "resource_limits_verified": True, "disposable_filesystem_verified": True,
                "required_capabilities_verified": True, "uid_non_root": True,
                "docker_socket_absent": True, "protected_mounts_absent": True,
            }), ""
        return 0, "ok", ""

    executor = DockerExecutor(DockerSandboxProfile("python:3.12-slim"), runner=fake, which=lambda _: "/docker")
    executor.verify_runtime()
    matrix = AttackMatrix(("a",), {})
    report = RuntimeReadiness.assess(executor.profile, executor, matrix)
    assert report.runtime_verified
    assert not report.attacks_verified
    assert not report.execution_authorized


def test_readiness_is_explicitly_authorized_only_after_all_gates():
    profile = DockerSandboxProfile("python:3.12-slim")
    executor = DockerExecutor(profile, which=lambda _: None)
    matrix = AttackMatrix(("a",), {})
    matrix.record(AttackResult("a", "a", AttackStatus.BLOCKED, "evidence"))
    # A policy-complete matrix alone never fabricates runtime evidence.
    report = RuntimeReadiness.assess(profile, executor, matrix)
    assert report.attacks_verified
    assert not report.execution_authorized
