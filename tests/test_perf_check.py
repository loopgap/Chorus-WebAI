from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_perf_check_passes():
    root = Path(__file__).resolve().parents[1]
    py = sys.executable
    # Run perf_check.py using the same python interpreter as the test
    proc = subprocess.run([py, "perf_check.py"], cwd=root, capture_output=True, text=True)

    # Assert return code is 0
    assert proc.returncode == 0, f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"

    # Parse JSON from stdout
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse JSON from stdout: {e}\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}")

    assert payload["failed"] == []
