from core.analysis import Analyzer, AnalyzerRunner
from core.analysis.model import Observation
from core.project import EventLog


class FailingAnalyzer(Analyzer):
    analyzer_id = "test.failing"
    version = "1.0"

    def run(self, inputs):
        yield Observation(
            id="obs-1",
            type="test",
            asset_id="asset-1",
            value=1,
            confidence=1.0,
            uncertainty=None,
            status="observed",
        )
        raise RuntimeError("boom")


def test_failed_run_commits_no_observation(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    result = AnalyzerRunner(log).run(FailingAnalyzer(), {})
    assert result.committed is False
    assert not any(e.event_type == "observation.created" for e in log.iter_events())
    assert any(e.event_type == "analysis.failed" for e in log.iter_events())
