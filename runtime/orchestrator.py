from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from protocol.events import EventEnvelope, EventType
from protocol.event_log import EventLog
from protocol.state_machine import ProtocolState, apply
from runtime.checkpoint import CheckpointStore, ExecutionCheckpoint
from protocol.validation import validate_event

@dataclass
class AgentProtocolRuntime:
    log: EventLog
    state: dict[str, ProtocolState]
    checkpoint_store: CheckpointStore | None = None

    @classmethod
    def create(cls, checkpoint_store: CheckpointStore | None = None) -> "AgentProtocolRuntime":
        return cls(EventLog(), {}, checkpoint_store)

    def ingest(self, event: EventEnvelope) -> ProtocolState:
        validate_event(event)
        current=self.state.get(event.task_id)
        if current is None:
            if event.event_type is not EventType.TASK_CREATED: raise ValueError("first event must be TASK_CREATED")
            current=ProtocolState.NEW
        next_state=apply(current,event)
        self.log.append(event)
        self.state[event.task_id]=next_state
        return next_state

    def save_checkpoint(self, checkpoint: ExecutionCheckpoint) -> None:
        if self.checkpoint_store is None:
            raise RuntimeError("checkpoint_store is not configured")
        self.checkpoint_store.save(checkpoint)

    def resume_checkpoint(self, task_id: str) -> ExecutionCheckpoint | None:
        if self.checkpoint_store is None:
            return None
        checkpoint = self.checkpoint_store.load()
        if checkpoint is None or checkpoint.task_id != task_id:
            return None
        return checkpoint

    def make_event(self, *, event_type: EventType, task_id: str, issuer: str,
                   correlation_id: str, payload: dict, evidence_refs=()) -> EventEnvelope:
        canonical=json.dumps({"event_type":event_type.value,"task_id":task_id,"issuer":issuer,
                              "correlation_id":correlation_id,"payload":payload},sort_keys=True,separators=(",",":"),ensure_ascii=False)
        digest=sha256(canonical.encode()).hexdigest()[:20]
        return EventEnvelope("evt_"+digest,event_type,task_id,issuer,correlation_id,"idem_"+digest,payload,tuple(evidence_refs))
