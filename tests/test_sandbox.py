from evo_kernel.sandbox import IsolationStatus, SandboxUnavailable, require_isolation


def test_unavailable_sandbox_fails_closed():
    status = IsolationStatus(available=False, reason="docker_not_installed")
    try:
        require_isolation(status)
    except SandboxUnavailable as exc:
        assert "FAIL_CLOSED" in str(exc)
    else:
        raise AssertionError("sandbox indisponível não pode ser aceito")


def test_docker_presence_without_effective_profile_fails_closed():
    status = IsolationStatus(
        available=True,
        reason="docker_present_runtime_profile_unverified",
        docker_version="Docker version test",
    )
    try:
        require_isolation(status)
    except SandboxUnavailable:
        pass
    else:
        raise AssertionError("Docker disponível sem perfil efetivamente verificado foi aceito")


def test_all_properties_are_required_for_approval():
    status = IsolationStatus(
        available=True,
        reason="verified",
        rootless_or_userns=True,
        no_new_privileges=True,
        network_disabled=True,
        seccomp_present=True,
        resource_limits_verified=True,
        disposable_filesystem_verified=True,
        required_capabilities_verified=True,
    )
    assert status.all_required_properties_verified
    require_isolation(status)
