import json

import pytest

from evo_kernel.docker_executor import DockerExecutor, DockerExecutorError
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
        DockerSandboxProfile(image="python:3.12-slim"),
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
        DockerSandboxProfile(image="python:3.12-slim"),
        runner=runner, which=lambda _: "/usr/bin/docker",
    )
    with pytest.raises(DockerExecutorError, match="invariantes"):
        executor.verify_runtime()


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
        DockerSandboxProfile(image="python:3.12-slim"),
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
        DockerSandboxProfile(image="python:3.12-slim"),
        which=lambda _: None,
    )
    with pytest.raises(DockerExecutorError):
        executor.run(())
    with pytest.raises(DockerExecutorError):
        executor.run(("python\x00",))
