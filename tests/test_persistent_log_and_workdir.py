import json

import pytest

from evo_kernel.persistent_log import KernelLog
from evo_kernel.sandbox import SandboxEnvError, build_minimal_env, make_isolated_workdir


def test_persistent_log_survives_reopen_and_reports_local_status(tmp_path):
    path = tmp_path / "kernel.jsonl"
    log = KernelLog(path)
    log.append("start", {"generation": 0})
    log.append("stop", {"generation": 0})
    reopened = KernelLog(path)
    reopened.verify_chain()
    assert reopened.integrity_status() == "TAMPER_EVIDENT_LOCAL_ONLY"
    assert len(reopened.all_entries()) == 2
    assert len(reopened.chain_head_hash) == 64


def test_persistent_log_detects_payload_tampering_after_restart(tmp_path):
    path = tmp_path / "kernel.jsonl"
    log = KernelLog(path)
    log.append("event", {"value": 1})
    raw = json.loads(path.read_text().splitlines()[0])
    raw["payload"]["value"] = 2
    path.write_text(json.dumps(raw) + "\n")
    reopened = KernelLog(path)
    assert reopened.integrity_status() == "TAMPERED"


def test_workdir_rejects_absolute_and_parent_paths(tmp_path):
    with pytest.raises(SandboxEnvError):
        make_isolated_workdir(allowed_files={"../escape.txt": "x"}, base_tmp=tmp_path)
    with pytest.raises(SandboxEnvError):
        make_isolated_workdir(allowed_files={"/tmp/escape.txt": "x"}, base_tmp=tmp_path)


def test_workdir_accepts_only_declared_safe_files(tmp_path):
    workdir = make_isolated_workdir(
        allowed_files={"solution/main.py": "print('ok')"}, base_tmp=tmp_path
    )
    assert (workdir / "solution" / "main.py").read_text() == "print('ok')"
    assert list(workdir.rglob("*"))


def test_environment_rejects_unapproved_variables():
    with pytest.raises(SandboxEnvError):
        build_minimal_env(extra_env={"OPENAI_API_KEY": "secret"})
