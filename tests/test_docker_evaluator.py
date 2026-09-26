import json

import pytest

from evo_kernel.docker_evaluator import DockerEvaluator, RuntimeEvalCase
from evo_kernel.docker_executor import DockerExecutor, DockerExecutorError
from evo_kernel.docker_profile import DockerSandboxProfile
from evo_kernel.evaluator import TaskSpec


def runtime_evidence():
    return json.dumps({
        "rootless_or_userns": True, "no_new_privileges": True,
        "network_disabled": True, "seccomp_present": True,
        "resource_limits_verified": True, "disposable_filesystem_verified": True,
        "required_capabilities_verified": True, "uid_non_root": True,
        "docker_socket_absent": True, "protected_mounts_absent": True,
    })


def test_evaluator_fails_closed_without_docker():
    evaluator = DockerEvaluator(DockerExecutor(
        DockerSandboxProfile("python:3.12-slim"), which=lambda _: None,
    ))
    with pytest.raises(DockerExecutorError, match="FAIL_CLOSED"):
        evaluator.evaluate(
            TaskSpec("task-1", "arith", "v1", "hidden-1"),
            "print(input())",
            (RuntimeEvalCase("x", "x"),),
        )


def test_evaluator_returns_only_sanitized_result_and_never_sends_expected_output():
    calls = []

    def runner(argv, timeout, stdin):
        calls.append((tuple(argv), stdin))
        if argv[1] == "info":
            return 0, "ok", ""
        if any("rootless_or_userns" in arg for arg in argv):
            return 0, runtime_evidence(), ""
        assert "expected-secret" not in argv
        return 0, "x", ""

    evaluator = DockerEvaluator(DockerExecutor(
        DockerSandboxProfile("python:3.12-slim"),
        runner=runner, which=lambda _: "/usr/bin/docker",
    ))
    output = evaluator.evaluate(
        TaskSpec("task-1", "arith", "v1", "hidden-1"),
        "print(input())",
        (RuntimeEvalCase("x", "x"),),
    )
    assert output.result.passed
    assert output.result.hidden_tests_accessible_to_solution is False
    assert output.passed_per_case == (True,)
    assert calls[-1][1] == "x"
