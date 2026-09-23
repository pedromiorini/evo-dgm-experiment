from decimal import Decimal

import pytest

from evo_kernel.budget import Budget
from evo_kernel.dry_run import DryRunPipeline
from evo_kernel.exploratory import ExploratoryRun
from evo_kernel.gateway import GatewayPolicy
from evo_kernel.manifest import FrozenManifest


def make_run():
    manifest = FrozenManifest.freeze({
        "experiment_id": "f4-dry-run", "protocol_version": "1.1", "mode": "EXPLORATORY",
        "hypothesis": "pipeline de engenharia executa três gerações",
        "primary_metric": "task_success_rate", "cost_estimand": "CUSTO_POR_TAREFA_IGUAL",
        "max_total_cost": "1.00", "final_feedback": False,
        "llm": {"provider": "mock", "model": "mock-v1", "version": "1"},
        "security_profile": {"network": "deny", "sandbox": "docker"},
    })
    pipeline = DryRunPipeline(
        manifest=manifest,
        budget=Budget("1.00"),
        gateway=GatewayPolicy("mock", "mock-v1", "1", Decimal("0.2"), Decimal("0.9"), 128),
    )
    return ExploratoryRun(pipeline), pipeline


def test_f4_runs_three_b3_generations_without_execution():
    run, pipeline = make_run()
    summary = run.run(generations=3)
    assert summary.arm == "B3"
    assert len(summary.reports) == 3
    assert summary.all_not_executed
    assert summary.scientific_evidence == "INSUFFICIENT_EVIDENCE"
    assert pipeline.budget.calls == 3


def test_f4_requires_three_generations():
    run, _ = make_run()
    with pytest.raises(ValueError):
        run.run(generations=2)
