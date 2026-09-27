import pytest

from evo_kernel.attack_matrix import AttackGateError, AttackMatrix, AttackResult, AttackStatus


def test_unverified_attack_cannot_open_gate():
    matrix = AttackMatrix.required_runtime_matrix()
    matrix.mark_unverified("network_escape", "Docker ausente")
    with pytest.raises(AttackGateError):
        matrix.assert_gate_open()
    assert matrix.summary()["UNVERIFIED"] == 1


def test_missing_attack_cannot_open_gate():
    matrix = AttackMatrix(("a",), {})
    with pytest.raises(AttackGateError, match="sem resultado"):
        matrix.assert_gate_open()


def test_blocked_and_failed_closed_are_approvable():
    matrix = AttackMatrix(("a", "b", "c"), {})
    matrix.record(AttackResult("a", "a", AttackStatus.BLOCKED, "probe blocked"))
    matrix.record(AttackResult("b", "b", AttackStatus.FAILED_CLOSED, "gate stopped"))
    matrix.record(AttackResult("c", "c", AttackStatus.BLOCKED, "probe blocked"))
    matrix.assert_gate_open()


def test_detected_attack_cannot_open_gate():
    matrix = AttackMatrix(("a",), {})
    matrix.record(AttackResult("a", "a", AttackStatus.DETECTED, "exploit succeeded"))
    with pytest.raises(AttackGateError, match="não aprováveis"):
        matrix.assert_gate_open()


def test_duplicate_or_unknown_attack_is_rejected():
    matrix = AttackMatrix(("a",), {})
    result = AttackResult("a", "a", AttackStatus.BLOCKED, "evidence")
    matrix.record(result)
    with pytest.raises(AttackGateError):
        matrix.record(result)
    with pytest.raises(AttackGateError):
        matrix.record(AttackResult("unknown", "unknown", AttackStatus.BLOCKED, "evidence"))
