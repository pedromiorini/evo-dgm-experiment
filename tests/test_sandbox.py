from evo_kernel.sandbox import IsolationStatus, SandboxUnavailable, require_isolation


def test_unavailable_sandbox_fails_closed():
    status = IsolationStatus(available=False, reason="docker_not_installed")
    try:
        require_isolation(status)
    except SandboxUnavailable as exc:
        assert "FAIL_CLOSED" in str(exc)
    else:
        raise AssertionError("sandbox indisponível não pode ser aceito")
