from decimal import Decimal
from pathlib import Path

import pytest

from evo_kernel.budget import Budget, BudgetExceeded
from evo_kernel.docker_profile import DockerProfileError, DockerSandboxProfile
from evo_kernel.evaluator import EvaluatorBoundary, EvaluatorBoundaryError, EvaluationResult, TaskSpec, TaskValidity
from evo_kernel.gateway import GatewayDenied, GatewayExchange, GatewayPolicy


def policy():
    return GatewayPolicy(
        provider="mock",
        model="mock-v1",
        version="1",
        temperature=Decimal("0.2"),
        top_p=Decimal("0.9"),
        max_tokens=128,
        allowed_tools=(),
    )


def test_gateway_records_hashes_and_consumes_budget():
    budget = Budget("1.00")
    exchange = GatewayExchange.record(
        policy=policy(),
        request={"messages": [{"role": "user", "content": "task"}]},
        response={"content": "proposal"},
        tokens=10,
        cost="0.25",
        cassette_id="cassette-1",
        budget=budget,
    )
    assert exchange.request_hash and exchange.response_hash
    assert budget.spent == Decimal("0.25")


def test_gateway_rejects_endpoint_or_model_override():
    with pytest.raises(GatewayDenied):
        policy().validate_request({"messages": [], "endpoint": "https://evil.invalid"})
    with pytest.raises(GatewayDenied):
        policy().validate_request({"messages": [], "temperature": Decimal("1.0")})


def test_gateway_budget_failure_is_closed():
    with pytest.raises(BudgetExceeded):
        GatewayExchange.record(
            policy=policy(), request={"messages": []}, response={}, tokens=1,
            cost="1.01", cassette_id="cassette-1", budget=Budget("1.00"),
        )


def test_evaluator_roots_must_be_separate():
    boundary = EvaluatorBoundary(Path("/tmp/solution"), Path("/tmp/evaluator"), Path("/tmp/holdout"))
    contract = boundary.build_transport_contract()
    assert contract["holdout_to_solution"] == "forbidden"
    with pytest.raises(EvaluatorBoundaryError):
        EvaluatorBoundary(Path("/tmp/a"), Path("/tmp/a/evaluator"), Path("/tmp/holdout")).validate_separation()


def test_evaluator_result_rejects_hidden_test_exposure():
    TaskSpec("t1", "family-a", "v1", "hidden-1").validate()
    result = EvaluationResult("t1", TaskValidity.PASS, True, "hash", hidden_tests_accessible_to_solution=True)
    with pytest.raises(EvaluatorBoundaryError):
        result.validate()


def test_docker_profile_is_restrictive_and_non_executing():
    args = DockerSandboxProfile("candidate-image").command_args()
    assert "--network=none" in args
    assert "--read-only" in args
    assert "--cap-drop=ALL" in args
    with pytest.raises(DockerProfileError):
        DockerSandboxProfile("candidate-image", network="bridge").command_args()
