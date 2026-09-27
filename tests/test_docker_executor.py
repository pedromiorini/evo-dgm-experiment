import json

import pytest

from evo_kernel.docker_executor import DockerExecutor, DockerExecutorError, mountpoints_have_no_protected_targets
from evo_kernel.docker_profile import DockerSandboxProfile


def evidence(**overrides):
    values = {
        "rootless_or_userns": True,
        "no_new_privileges": True,
        "network_disabled": True,
        "seccomp_present": True,
        "resource_limits_verified": True,
        "disposable_filesystem_verified": True,
        "required_capabilities_verified": True,
        "uid_non_root": True,
        "docker_socket_absent": True,
        "protected_mounts_absent": True,
    }
    values.update(overrides)
    return json.dumps(values)


def test_executor_fails_closed_without_docker():
    executor = DockerExecutor(
        DockerSandboxProfile(image="python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f"),
        which=lambda _: None,
    )
    with pytest.raises(DockerExecutorError, match="FAIL_CLOSED"):
        executor.verify_runtime()


def test_executor_rejects_incomplete_or_false_runtime_evidence():
    calls = []

    def runner(argv, timeout, stdin):
        calls.append(tuple(argv))
        if argv[1] == "info":
            return 0, "ok", ""
        return 0, evidence(network_disabled=False), ""

    executor = DockerExecutor(
        DockerSandboxProfile(image="python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f"),
        runner=runner, which=lambda _: "/usr/bin/docker",
    )
    with pytest.raises(DockerExecutorError, match="invariantes"):
        executor.verify_runtime()


def test_runtime_evidence_contains_identity_metadata():
    def runner(argv, timeout, stdin):
        if argv[1] == "info":
            return 0, "29.1.3\n", ""
        return 0, evidence(), ""

    executor = DockerExecutor(
        DockerSandboxProfile(image="python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f"),
        runner=runner, which=lambda _: "/usr/bin/docker",
    )
    result = executor.verify_runtime()
    assert result.docker_server_version == "29.1.3"
    assert result.image_digest.startswith("sha256:")
    assert result.profile_hash
    assert result.probe_version == "runtime-probe-v2"
    assert result.timestamp.endswith("+00:00")
    assert len(result.runtime_fingerprint) == 64


def test_run_revalidates_when_runtime_fingerprint_changes():
    versions = iter(("29.1.3\n", "29.1.4\n", "29.1.4\n"))
    calls = []

    def runner(argv, timeout, stdin):
        calls.append(tuple(argv))
        if argv[1] == "info":
            return 0, next(versions), ""
        return 0, evidence(), ""

    executor = DockerExecutor(
        DockerSandboxProfile(image="python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f"),
        runner=runner, which=lambda _: "/usr/bin/docker",
    )
    executor.verify_runtime()
    executor.run(("python3", "-c", "print('ok')"))
    assert sum(argv[1] == "info" for argv in calls) == 3


def test_executor_requires_probe_before_run_and_forwards_stdin():
    calls = []

    def runner(argv, timeout, stdin):
        calls.append((tuple(argv), stdin))
        if argv[1] == "info":
            return 0, "ok", ""
        if any("rootless_or_userns" in arg for arg in argv):
            return 0, evidence(), ""
        return 0, "result", ""

    executor = DockerExecutor(
        DockerSandboxProfile(image="python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f"),
        runner=runner, which=lambda _: "/usr/bin/docker",
    )
    result = executor.run(("python3", "-c", "print('ok')"), stdin_data="input")
    assert result.stdout == "result"
    run_argv, run_stdin = calls[-1]
    assert "--network=none" in run_argv
    assert "--security-opt=no-new-privileges" in run_argv
    assert "--cap-drop=ALL" in run_argv
    assert run_stdin == "input"


def test_executor_does_not_accept_empty_or_nul_command():
    executor = DockerExecutor(
        DockerSandboxProfile(image="python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f"),
        which=lambda _: None,
    )
    with pytest.raises(DockerExecutorError):
        executor.run(())
    with pytest.raises(DockerExecutorError):
        executor.run(("python\x00",))


def test_mount_check_ignores_docker_source_path_when_target_is_safe():
    safe = "126 91 254:0 /var/lib/docker/containers/id/hosts /etc/hosts ro - ext4 /dev/root rw"
    protected = "127 91 254:0 /dev/root /workspace ro - ext4 /dev/root rw"
    assert mountpoints_have_no_protected_targets(safe)
    assert not mountpoints_have_no_protected_targets(protected)
