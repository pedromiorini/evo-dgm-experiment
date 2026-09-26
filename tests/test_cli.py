import json

from evo_kernel.cli import main


def parse_output(capsys):
    return json.loads(capsys.readouterr().out)


def test_validate_is_fail_closed_without_docker(capsys):
    assert main(["validate"]) == 0
    output = parse_output(capsys)
    assert output["manifest"] == "VALID"
    assert output["sandbox"] == "FAIL_CLOSED"


def test_run_and_report_are_dry_run(capsys):
    assert main(["run", "--generations", "3"]) == 0
    run_output = parse_output(capsys)
    assert run_output["generations"] == 3
    assert run_output["execution_performed"] is False
    assert main(["report"]) == 0
    report_output = parse_output(capsys)
    assert report_output["scientific_evidence"] == "INSUFFICIENT_EVIDENCE"


def test_inspect_lineage_replay_and_stop(capsys):
    assert main(["inspect"]) == 0
    assert parse_output(capsys)["genome_execution"] == "BLOCKED"
    assert main(["lineage"]) == 0
    assert parse_output(capsys)["status"] == "AVAILABLE"
    assert main(["replay"]) == 0
    assert parse_output(capsys)["replay"] == "REPLAY_WITH_RECORDED_LLM_CASSETTES"
    assert main(["stop"]) == 0
    assert parse_output(capsys)["stop"] == "NO_ACTIVE_EXECUTION"


def test_readiness_and_attack_matrix_are_inspection_only(capsys):
    assert main(["readiness"]) == 0
    readiness = parse_output(capsys)
    assert readiness["policy_ready"] is True
    assert readiness["runtime_verified"] is False
    assert readiness["execution_authorized"] is False
    assert main(["attack-matrix"]) == 0
    matrix = parse_output(capsys)
    assert matrix["execution"] == "NOT_RUN"
    assert matrix["gate"] == "BLOCKED"
