from evo_kernel.manifest import FrozenManifest, ManifestError
from evo_kernel.permissions import MutationProposal, PermissionDenied
from evo_kernel.provenance import LineageRecord, ProvenanceError
from evo_kernel.validity import CandidateValidity, PromotionDenied, ValidityState


def manifest_data():
    return {
        "experiment_id": "exp-001",
        "protocol_version": "1.1",
        "mode": "EXPLORATORY",
        "hypothesis": "pipeline executa tarefas verificadas",
        "primary_metric": "task_success_rate",
        "cost_estimand": "CUSTO_POR_TAREFA_IGUAL",
        "max_total_cost": "100.00",
        "final_feedback": False,
        "llm": {"provider": "mock", "model": "mock-v1", "version": "1"},
        "security_profile": {"network": "deny", "sandbox": "docker-rootless"},
    }


def test_manifest_freezes_and_detects_mutation():
    manifest = FrozenManifest.freeze(manifest_data())
    manifest.verify()
    manifest.data["mode"] = "CONFIRMATORY"
    try:
        manifest.verify()
    except ManifestError:
        pass
    else:
        raise AssertionError("manifesto adulterado foi aceito")


def test_manifest_requires_final_feedback_false():
    data = manifest_data()
    data["final_feedback"] = True
    try:
        FrozenManifest.freeze(data)
    except ManifestError:
        pass
    else:
        raise AssertionError("manifesto com feedback final foi aceito")


def valid_proposal(**overrides):
    values = dict(
        change_id="c1",
        parent_id="v0",
        hypothesis="reduzir alocação",
        diff_hash="a" * 64,
        files=("genome.py",),
    )
    values.update(overrides)
    return MutationProposal(**values)


def test_permission_allowlist_rejects_protected_paths_and_permissions():
    valid_proposal().validate()
    for proposal in (
        valid_proposal(files=("evaluator/checks.py",)),
        valid_proposal(requested_permissions=("network",)),
        valid_proposal(files=("../escape.py",)),
    ):
        try:
            proposal.validate()
        except PermissionDenied:
            pass
        else:
            raise AssertionError("proposta insegura foi aceita")


def test_promotion_requires_all_validity_dimensions():
    candidate = CandidateValidity(functional=True, security=True, experimental=False)
    assert candidate.state == ValidityState.SECURITY_VALID
    try:
        candidate.require_promotion()
    except PromotionDenied:
        pass
    else:
        raise AssertionError("candidato sem validade experimental foi promovido")
    assert CandidateValidity(True, True, True).state == ValidityState.PROMOTED


def test_lineage_hash_detects_tampering():
    record = LineageRecord.create(
        variant_id="v1",
        parent_id="v0",
        generation=1,
        seed=7,
        genome_hash="b" * 64,
        diff_hash="c" * 64,
    )
    record.verify()
    tampered = LineageRecord(
        variant_id=record.variant_id,
        parent_id=record.parent_id,
        generation=99,
        seed=record.seed,
        genome_hash=record.genome_hash,
        diff_hash=record.diff_hash,
        timestamp=record.timestamp,
        record_hash=record.record_hash,
    )
    try:
        tampered.verify()
    except ProvenanceError:
        pass
    else:
        raise AssertionError("provenance adulterada foi aceita")
