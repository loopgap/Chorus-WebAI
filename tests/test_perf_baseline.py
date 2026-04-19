"""Performance baseline tests for critical operations.

These tests verify that key operations meet their performance thresholds.
They are designed to catch performance regressions.
"""

from __future__ import annotations

import os
import time

import pytest


# Performance thresholds (in seconds)
THRESHOLDS = {
    "import_web_app_seconds": 1.0,
    "build_ui_seconds": 15.0,
    "build_guide_seconds": 0.4,
    "build_api_doc_seconds": 0.4,
    "history_table_seconds": 0.6,
}

# CI multiplier - CI environments are typically slower
IS_CI = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"
CI_MULTIPLIER = 5.0 if IS_CI else 1.0


def get_effective_threshold(key: str) -> float:
    """Get the effective threshold, accounting for CI environment."""
    return THRESHOLDS[key] * CI_MULTIPLIER


class TestImportPerformance:
    """Test import time performance."""

    def test_import_web_app_time(self):
        """Test that importing web_app module is fast enough."""
        t0 = time.perf_counter()
        import web_app  # noqa: F401

        import_time = time.perf_counter() - t0
        threshold = get_effective_threshold("import_web_app_seconds")

        assert import_time < threshold, f"Import time {import_time:.3f}s exceeds threshold {threshold:.3f}s"


class TestBuildUIPerformance:
    """Test UI build performance."""

    def test_build_ui_time(self, tmp_path, monkeypatch):
        """Test that build_ui completes within time limit."""
        # Ensure state directory exists for the app
        monkeypatch.setenv("STATE_DIR", str(tmp_path))

        import web_app as app

        t0 = time.perf_counter()
        app.build_ui()
        build_time = time.perf_counter() - t0

        threshold = get_effective_threshold("build_ui_seconds")
        assert build_time < threshold, f"build_ui time {build_time:.3f}s exceeds threshold {threshold:.3f}s"


class TestHelperFunctionPerformance:
    """Test helper function performance."""

    @pytest.fixture
    def app(self):
        """Import web_app module once for all tests in this class."""
        import web_app

        return web_app

    def test_build_guide_markdown_time(self, app, tmp_path, monkeypatch):
        """Test _build_guide_markdown performance."""
        monkeypatch.setenv("STATE_DIR", str(tmp_path))

        t0 = time.perf_counter()
        app._build_guide_markdown()
        elapsed = time.perf_counter() - t0

        threshold = get_effective_threshold("build_guide_seconds")
        assert elapsed < threshold, f"_build_guide_markdown time {elapsed:.3f}s exceeds threshold {threshold:.3f}s"

    def test_build_api_doc_text_time(self, app, tmp_path, monkeypatch):
        """Test _build_api_doc_text performance."""
        monkeypatch.setenv("STATE_DIR", str(tmp_path))

        t0 = time.perf_counter()
        app._build_api_doc_text()
        elapsed = time.perf_counter() - t0

        threshold = get_effective_threshold("build_api_doc_seconds")
        assert elapsed < threshold, f"_build_api_doc_text time {elapsed:.3f}s exceeds threshold {threshold:.3f}s"

    def test_history_table_time(self, app, tmp_path, monkeypatch):
        """Test _history_table performance."""
        monkeypatch.setenv("STATE_DIR", str(tmp_path))

        t0 = time.perf_counter()
        app._history_table("全部")
        elapsed = time.perf_counter() - t0

        threshold = get_effective_threshold("history_table_seconds")
        assert elapsed < threshold, f"_history_table time {elapsed:.3f}s exceeds threshold {threshold:.3f}s"


class TestBaselineSummary:
    """Summary test that reports all baseline metrics."""

    def test_full_baseline_metrics(self, tmp_path, monkeypatch):
        """Run all performance checks and report metrics."""
        monkeypatch.setenv("STATE_DIR", str(tmp_path))

        metrics = {}

        # Import timing
        t0 = time.perf_counter()
        import web_app as app

        metrics["import_web_app_seconds"] = time.perf_counter() - t0

        # build_ui timing
        t0 = time.perf_counter()
        app.build_ui()
        metrics["build_ui_seconds"] = time.perf_counter() - t0

        # Helper function timings
        t0 = time.perf_counter()
        app._build_guide_markdown()
        metrics["build_guide_seconds"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        app._build_api_doc_text()
        metrics["build_api_doc_seconds"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        app._history_table("全部")
        metrics["history_table_seconds"] = time.perf_counter() - t0

        # Check all metrics
        failures = []
        for key, value in metrics.items():
            threshold = get_effective_threshold(key)
            if value > threshold:
                failures.append(f"{key}: {value:.3f}s > {threshold:.3f}s")

        assert not failures, "Performance failures:\n  " + "\n  ".join(failures)
