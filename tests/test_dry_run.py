from decimal import Decimal

from evo_kernel.budget import Budget
from evo_kernel.dry_run import DryRunPipeline
from evo_kernel.gateway import GatewayPolicy
from evo_kernel.manifest import FrozenManifest
from evo_kernel.mock_llm import MockScenario
from evo_kernel.task_validation import TaskDefinition, TaskValidationResult
from evo_kernel.validity import ValidityState


def make_manifest():
    return FrozenManifest.freeze({
        "experiment_id": "dry-run-1", "protocol_version": "1.1", "mode": "EXPLORATORY",
        "hypothesis": "pipeline local funciona", "primary_metric": "task_success_rate",
        "cost_estimand": "CUSTO_POR_TAREFA_IGUAL", "max_total_cost": "1.00",
        "final_feedback": False, "llm": {"provider": "mock", "model": "mock-v1", "version": "1"},
        "security_profile": {"network": "deny", "sandbox": "docker"},
    })


def make_pipeline():
    return DryRunPipeline(
        manifest=make_manifest(),
        budget=Budget(Decimal("1.00")),
        gateway=GatewayPolicy("mock", "mock-v1", "1", Decimal("0.2"), Decimal("0.9"), 128),
    )


def valid_task_result():
    return TaskValidationResult(True, True, True, True, True)


def test_dry_run_records_controls_without_execution():
    report = make_pipeline().run(
        task=TaskDefinition("task-1", "family-a", "v1"),
        task_result=valid_task_result(),
        scenario=MockScenario.VALID_MUTATION,
    )
    assert report.proposal_accepted is True
    assert report.gateway_recorded is True
    assert report.cassette_verified is True
    assert report.lineage_verified is True
    assert report.execution_performed is False
    assert report.validity_state == ValidityState.NOT_EXECUTED
    assert report.evidence_state == "INSUFFICIENT_EVIDENCE"


def test_dry_run_preserves_historical_data_boundary():
    report = make_pipeline().run(
        task=TaskDefinition("task-2", "family-a", "v1"),
        task_result=valid_task_result(),
        scenario=MockScenario.HISTORICAL_INJECTION,
    )
    assert report.history_is_data is True
    assert report.execution_performed is False


def test_dry_run_records_malformed_response_without_promoting():
    report = make_pipeline().run(
        task=TaskDefinition("task-3", "family-a", "v1"),
        task_result=valid_task_result(),
        scenario=MockScenario.MALFORMED_RESPONSE,
    )
    assert report.proposal_accepted is False
    assert report.gateway_recorded is False
    assert report.rejection_reason == "malformed_response"
    assert report.validity_state == ValidityState.NOT_EXECUTED
