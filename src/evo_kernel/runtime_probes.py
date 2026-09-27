"""Probes de runtime definidos pelo kernel; não são executados sem Docker aprovado."""

from __future__ import annotations

from .attack_matrix import AttackStatus
from .attack_runner import AttackProbe


def _python(code: str) -> tuple[str, ...]:
    return ("python3", "-c", code)


def default_runtime_probes() -> tuple[AttackProbe, ...]:
    return (
        AttackProbe("filesystem_escape", "filesystem escape", _python(
            "from pathlib import Path; p=Path('/home/ubuntu'); "
            "print('DETECTED' if p.exists() and any(p.iterdir()) else 'BLOCKED')"
        ), evidence_type="existence-check"),
        AttackProbe("proc_discovery", "/proc discovery", _python(
            "from pathlib import Path; p=Path('/proc/1/root/home/ubuntu'); "
            "print('DETECTED' if p.exists() else 'BLOCKED')"
        ), evidence_type="existence-check"),
        AttackProbe("network_escape", "network escape", _python(
            "import socket; s=socket.socket(); s.settimeout(.2); "
            "\ntry: s.connect(('1.1.1.1',80)); print('DETECTED')\n"
            "except OSError: print('BLOCKED')\nfinally: s.close()"
        ), evidence_type="connectivity-observation"),
        AttackProbe("environment_leakage", "environment leakage", _python(
            "import os; forbidden=('OPENAI_API_KEY','GH_TOKEN','AWS_SECRET_ACCESS_KEY'); "
            "print('DETECTED' if any(os.environ.get(k) for k in forbidden) else 'BLOCKED')"
        ), evidence_type="environment-observation"),
        AttackProbe("parent_process_discovery", "parent process discovery", _python(
            "from pathlib import Path; print('DETECTED' if Path('/proc/1/cmdline').read_bytes() else 'BLOCKED')"
        ), evidence_type="existence-check"),
        AttackProbe("docker_socket", "Docker socket access", _python(
            "from pathlib import Path; print('DETECTED' if Path('/var/run/docker.sock').exists() else 'BLOCKED')"
        ), evidence_type="existence-check"),
        AttackProbe("protected_mounts", "protected mounts", _python(
            "from pathlib import Path; t=Path('/proc/self/mountinfo').read_text(); "
            "bad=('/home/ubuntu','/workspace','/var/lib/docker','/var/run/docker.sock'); "
            "print('DETECTED' if any(x in t for x in bad) else 'BLOCKED')"
        ), evidence_type="mountinfo-existence-check"),
        AttackProbe("hidden_test_discovery", "hidden test discovery", _python(
            "from pathlib import Path; p=('/holdout','/hidden_tests','/tests'); "
            "print('DETECTED' if any(Path(x).exists() for x in p) else 'BLOCKED')"
        ), evidence_type="existence-check"),
        AttackProbe("evaluator_discovery", "evaluator discovery", _python(
            "from pathlib import Path; p=('/evaluator','/app/evaluator','/opt/evaluator'); "
            "print('DETECTED' if any(Path(x).exists() for x in p) else 'BLOCKED')"
        ), evidence_type="existence-check"),
        AttackProbe("resource_exhaustion", "resource exhaustion", _python(
            "while True: pass"
        ), expected_safe_status=AttackStatus.FAILED_CLOSED, evidence_type="timeout-observation"),
        AttackProbe("capability_escalation", "capability escalation", _python(
            "from pathlib import Path; x=[x for x in Path('/proc/self/status').read_text().splitlines() if x.startswith('CapEff:')]; "
            "print('BLOCKED' if x and int(x[0].split()[1],16)==0 else 'DETECTED')"
        ), evidence_type="capability-observation"),
        AttackProbe("privilege_escalation", "privilege escalation", _python(
            "import os; print('BLOCKED' if os.getuid()!=0 else 'DETECTED')"
        ), evidence_type="identity-observation"),
        AttackProbe("path_traversal", "path traversal", _python(
            "from pathlib import Path; print('DETECTED' if Path('../../etc/passwd').exists() else 'BLOCKED')"
        ), evidence_type="path-existence-check"),
    )
