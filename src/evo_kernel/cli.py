"""Interface CLI mínima da SPEC; não executa genomas nem containers."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal

from .budget import Budget
from .cassette import Cassette
from .dry_run import DryRunPipeline
from .exploratory import ExploratoryRun
from .gateway import GatewayPolicy
from .manifest import FrozenManifest
from .sandbox import verify_docker_isolation


def demo_pipeline() -> DryRunPipeline:
    manifest = FrozenManifest.freeze({
        "experiment_id": "cli-demo", "protocol_version": "1.1", "mode": "EXPLORATORY",
        "hypothesis": "validar pipeline de engenharia", "primary_metric": "task_success_rate",
        "cost_estimand": "CUSTO_POR_TAREFA_IGUAL", "max_total_cost": "10.00",
        "final_feedback": False, "llm": {"provider": "mock", "model": "mock-v1", "version": "1"},
        "security_profile": {"network": "deny", "sandbox": "docker"},
    })
    return DryRunPipeline(
        manifest=manifest,
        budget=Budget("10.00"),
        gateway=GatewayPolicy("mock", "mock-v1", "1", Decimal("0.2"), Decimal("0.9"), 128),
    )


def command_validate(_: argparse.Namespace) -> int:
    pipeline = demo_pipeline()
    status = verify_docker_isolation()
    print(json.dumps({
        "manifest": "VALID",
        "mode": pipeline.manifest.data["mode"],
        "sandbox": "AVAILABLE" if status.available else "FAIL_CLOSED",
        "reason": status.reason,
    }, ensure_ascii=False))
    return 0


def command_run(args: argparse.Namespace) -> int:
    summary = ExploratoryRun(demo_pipeline()).run(generations=args.generations)
    print(json.dumps({
        "arm": summary.arm,
        "generations": len(summary.reports),
        "execution_performed": summary.all_not_executed is False,
        "scientific_evidence": summary.scientific_evidence,
    }, ensure_ascii=False))
    return 0


def command_inspect(_: argparse.Namespace) -> int:
    status = verify_docker_isolation()
    print(json.dumps({
        "global_state": "IN_PROGRESS",
        "mode": "EXPLORATORY",
        "genome_execution": "BLOCKED",
        "sandbox_reason": status.reason,
    }, ensure_ascii=False))
    return 0


def command_lineage(_: argparse.Namespace) -> int:
    print(json.dumps({"lineage": "kernel-generated", "source": "dry-run", "status": "AVAILABLE"}))
    return 0


def command_replay(_: argparse.Namespace) -> int:
    cassette = Cassette.create(
        cassette_id="cli-replay", provider="mock", model="mock-v1", version="1",
        request={"messages": [{"role": "user", "content": "demo"}]},
        response={"content": "recorded"}, tokens=1, cost="0.00",
    )
    response = cassette.replay(cassette.request)
    print(json.dumps({"replay": "REPLAY_WITH_RECORDED_LLM_CASSETTES", "response": response}, ensure_ascii=False))
    return 0


def command_stop(_: argparse.Namespace) -> int:
    print(json.dumps({"stop": "NO_ACTIVE_EXECUTION", "genome_execution": "BLOCKED"}, ensure_ascii=False))
    return 0


def command_report(args: argparse.Namespace) -> int:
    return command_run(argparse.Namespace(generations=args.generations))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evo-kernel")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate").set_defaults(func=command_validate)
    run = sub.add_parser("run", help="executa somente dry-run exploratório")
    run.add_argument("--generations", type=int, default=3)
    run.set_defaults(func=command_run)
    sub.add_parser("inspect").set_defaults(func=command_inspect)
    sub.add_parser("lineage").set_defaults(func=command_lineage)
    sub.add_parser("replay").set_defaults(func=command_replay)
    sub.add_parser("stop").set_defaults(func=command_stop)
    report = sub.add_parser("report")
    report.add_argument("--generations", type=int, default=3)
    report.set_defaults(func=command_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
