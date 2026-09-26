from evo_kernel.runtime_probes import default_runtime_probes


def test_default_runtime_probes_cover_required_attack_ids():
    probes = default_runtime_probes()
    ids = [probe.attack_id for probe in probes]
    assert len(probes) == 13
    assert len(set(ids)) == 13
    assert {
        "filesystem_escape", "proc_discovery", "network_escape", "environment_leakage",
        "parent_process_discovery", "docker_socket", "protected_mounts",
        "hidden_test_discovery", "evaluator_discovery", "resource_exhaustion",
        "capability_escalation", "privilege_escalation", "path_traversal",
    } == set(ids)
    for probe in probes:
        probe.validate()
        assert all("\x00" not in arg for arg in probe.command)
