import pytest

from evo_kernel.critical_integrity import (
    CriticalIntegrityError,
    compute_kernel_hash,
    verify_before_critical_operation,
)
from evo_kernel.persistent_log import KernelLog


def checks():
    return {
        "manifest_hash": lambda: True,
        "dependency_hash": lambda: True,
        "permissions": lambda: True,
        "evaluator_state": lambda: True,
    }


def test_critical_integrity_passes_only_with_all_checks(tmp_path):
    kernel_dir = tmp_path / "kernel"
    kernel_dir.mkdir()
    (kernel_dir / "a.py").write_text("VALUE = 1\n")
    log = KernelLog(tmp_path / "log.jsonl")
    report = verify_before_critical_operation(
        kernel_dir=kernel_dir,
        expected_kernel_hash=compute_kernel_hash(kernel_dir),
        log=log,
        extra_checks=checks(),
    )
    assert report.all_verified


def test_wrong_kernel_hash_fails_closed(tmp_path):
    kernel_dir = tmp_path / "kernel"
    kernel_dir.mkdir()
    (kernel_dir / "a.py").write_text("VALUE = 1\n")
    with pytest.raises(CriticalIntegrityError, match="kernel"):
        verify_before_critical_operation(
            kernel_dir=kernel_dir, expected_kernel_hash="0" * 64,
            log=KernelLog(tmp_path / "log.jsonl"), extra_checks=checks(),
        )


def test_missing_critical_check_fails_closed(tmp_path):
    kernel_dir = tmp_path / "kernel"
    kernel_dir.mkdir()
    (kernel_dir / "a.py").write_text("VALUE = 1\n")
    incomplete = checks()
    incomplete.pop("evaluator_state")
    with pytest.raises(CriticalIntegrityError, match="evaluator_state"):
        verify_before_critical_operation(
            kernel_dir=kernel_dir,
            expected_kernel_hash=compute_kernel_hash(kernel_dir),
            log=KernelLog(tmp_path / "log.jsonl"),
            extra_checks=incomplete,
        )


def test_failed_critical_check_fails_closed(tmp_path):
    kernel_dir = tmp_path / "kernel"
    kernel_dir.mkdir()
    (kernel_dir / "a.py").write_text("VALUE = 1\n")
    failed = checks()
    failed["permissions"] = lambda: False
    with pytest.raises(CriticalIntegrityError, match="permissions"):
        verify_before_critical_operation(
            kernel_dir=kernel_dir,
            expected_kernel_hash=compute_kernel_hash(kernel_dir),
            log=KernelLog(tmp_path / "log.jsonl"),
            extra_checks=failed,
        )


def test_tampered_log_fails_closed(tmp_path):
    kernel_dir = tmp_path / "kernel"
    kernel_dir.mkdir()
    (kernel_dir / "a.py").write_text("VALUE = 1\n")
    log_path = tmp_path / "log.jsonl"
    log = KernelLog(log_path)
    log.append("event", {"x": 1})
    log_path.write_text(log_path.read_text().replace('"x": 1', '"x": 2'))
    with pytest.raises(CriticalIntegrityError, match="log"):
        verify_before_critical_operation(
            kernel_dir=kernel_dir,
            expected_kernel_hash=compute_kernel_hash(kernel_dir),
            log=KernelLog(log_path),
            extra_checks=checks(),
        )
