"""Loop exploratório B3-only para validação de engenharia."""

from __future__ import annotations

from dataclasses import dataclass

from .dry_run import DryRunPipeline, DryRunReport
from .manifest import ManifestError
from .mock_llm import MockScenario
from .task_validation import TaskDefinition, TaskValidationResult


@dataclass(frozen=True)
class ExploratoryRunSummary:
    arm: str
    generations_requested: int
    reports: tuple[DryRunReport, ...]
    scientific_evidence: str = "INSUFFICIENT_EVIDENCE"

    @property
    def all_not_executed(self) -> bool:
        return all(not report.execution_performed for report in self.reports)


class ExploratoryRun:
    """Executa apenas a sequência de contratos do B3 exploratório."""

    def __init__(self, pipeline: DryRunPipeline) -> None:
        if pipeline.manifest.data.get("mode") != "EXPLORATORY":
            raise ManifestError("ExploratoryRun exige manifesto EXPLORATORY")
        self.pipeline = pipeline

    def run(self, *, generations: int = 3) -> ExploratoryRunSummary:
        if generations < 3:
            raise ValueError("F4 exige pelo menos três gerações")
        reports: list[DryRunReport] = []
        for generation in range(generations):
            report = self.pipeline.run(
                task=TaskDefinition(
                    task_id=f"task-generation-{generation}",
                    family="family-programming-io",
                    template_version="v1",
                ),
                task_result=TaskValidationResult(True, True, True, True, True),
                scenario=MockScenario.VALID_MUTATION,
                generation=generation,
            )
            reports.append(report)
        return ExploratoryRunSummary(
            arm="B3",
            generations_requested=generations,
            reports=tuple(reports),
        )
