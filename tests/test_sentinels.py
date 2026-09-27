import hashlib

import pytest

from evo_kernel.sentinels import SentinelError, SentinelObservation, SentinelRegistry


def test_sentinel_public_record_does_not_expose_secret():
    registry = SentinelRegistry()
    sentinel = registry.issue("hidden-1", "/protected/hidden-1")
    public = sentinel.public_record()
    assert "secret_digest" not in public
    assert sentinel.secret_digest not in repr(public)


def test_no_attempt_is_blocked_even_if_path_exists():
    registry = SentinelRegistry()
    registry.issue("hidden-1", "/protected/hidden-1")
    assert registry.observe(SentinelObservation("hidden-1", False, False, None)) == "BLOCKED"


def test_reading_correct_secret_is_detected():
    registry = SentinelRegistry()
    sentinel = registry.issue("hidden-1", "/protected/hidden-1")
    observation = SentinelObservation("hidden-1", True, True, sentinel.secret_digest)
    assert registry.observe(observation) == "DETECTED"


def test_open_without_verified_secret_is_unverified():
    registry = SentinelRegistry()
    registry.issue("hidden-1", "/protected/hidden-1")
    wrong_digest = hashlib.sha256(b"wrong").hexdigest()
    observation = SentinelObservation("hidden-1", True, True, wrong_digest)
    assert registry.observe(observation) == "UNVERIFIED"


def test_inconsistent_observation_is_rejected():
    registry = SentinelRegistry()
    registry.issue("hidden-1", "/protected/hidden-1")
    with pytest.raises(SentinelError):
        registry.observe(SentinelObservation("hidden-1", False, True, None))
