"""Transactional analyzer runner.

Observations are buffered until successful completion. A failed run records a
failure event without pretending that partial output is a completed analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..identity import new_id
from ..project.events import EventLog
from .base import Analyzer
from .model import Observation


@dataclass(frozen=True, slots=True)
class AnalysisRunResult:
    run_id: str
    observations: tuple[Observation, ...]
    committed: bool
    error_type: str | None = None


class AnalyzerRunner:
    def __init__(self, event_log: EventLog) -> None:
        self.event_log = event_log

    def run(self, analyzer: Analyzer, inputs: dict[str, Any]) -> AnalysisRunResult:
        run_id = new_id("analysis")
        buffered: list[Observation] = []
        try:
            for observation in analyzer.run(inputs):
                buffered.append(observation)
        except Exception as exc:
            self.event_log.append_new(
                event_id=new_id("evt"),
                event_type="analysis.failed",
                actor=f"analyzer:{analyzer.analyzer_id}@{analyzer.version}",
                payload={
                    "run_id": run_id,
                    "analyzer": {
                        "id": analyzer.analyzer_id,
                        "version": analyzer.version,
                        "code_hash": analyzer.identity.code_hash,
                        "config_hash": analyzer.identity.config_hash,
                    },
                    "error_type": type(exc).__name__,
                    "input_keys": sorted(inputs.keys()),
                },
            )
            return AnalysisRunResult(run_id, (), False, type(exc).__name__)

        for observation in buffered:
            self.event_log.append_new(
                event_id=new_id("evt"),
                event_type="observation.created",
                actor=f"analyzer:{analyzer.analyzer_id}@{analyzer.version}",
                payload=observation.to_dict(),
            )
        self.event_log.append_new(
            event_id=new_id("evt"),
            event_type="analysis.completed",
            actor=f"analyzer:{analyzer.analyzer_id}@{analyzer.version}",
            payload={"run_id": run_id, "observation_count": len(buffered)},
        )
        return AnalysisRunResult(run_id, tuple(buffered), True)
