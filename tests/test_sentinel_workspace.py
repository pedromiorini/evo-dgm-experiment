import os

import pytest

from evo_kernel.sentinel_workspace import SentinelWorkspace
from evo_kernel.sentinels import SentinelError, SentinelObservation


def test_workspace_creates_restricted_file_and_cleans_up(tmp_path):
    with SentinelWorkspace(base_dir=tmp_path) as workspace:
        sentinel = workspace.issue_file("hidden-tests")
        path = sentinel.protected_path
        assert os.stat(workspace.root).st_mode & 0o777 == 0o700
        assert os.stat(path).st_mode & 0o777 == 0o600
        assert workspace.verify_file_digest("hidden-tests") == sentinel.secret_digest
        assert sentinel.secret_digest not in repr(sentinel.public_record())
    assert not os.path.exists(path)


def test_workspace_does_not_expose_sentinel_to_unknown_id(tmp_path):
    with SentinelWorkspace(base_dir=tmp_path) as workspace:
        workspace.issue_file("evaluator")
        with pytest.raises(SentinelError):
            workspace.verify_file_digest("other")
