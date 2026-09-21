#!/usr/bin/env python3
"""Minimal request-correlated JSONL trace for runtime experiments."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TextIO


@dataclass(slots=True)
class RuntimeEvent:
    timestamp_ns: int
    event: str
    request_id: str | None = None
    iteration_id: int | None = None
    scheduled_tokens: int | None = None
    running_count: int | None = None
    waiting_count: int | None = None
    token_budget_remaining: int | None = None
    preempted: bool | None = None


class JsonlRuntimeTrace:
    """Small append-only trace with buffered writes."""

    def __init__(self, path: str | Path, flush_every: int = 64) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.flush_every = max(int(flush_every), 1)
        self._fh: TextIO = self.path.open("a", encoding="utf-8")
        self._pending = 0

    def record(
        self,
        event: str,
        *,
        request_id: str | None = None,
        iteration_id: int | None = None,
        scheduled_tokens: int | None = None,
        running_count: int | None = None,
        waiting_count: int | None = None,
        token_budget_remaining: int | None = None,
        preempted: bool | None = None,
    ) -> None:
        item = RuntimeEvent(
            timestamp_ns=time.perf_counter_ns(),
            event=event,
            request_id=request_id,
            iteration_id=iteration_id,
            scheduled_tokens=scheduled_tokens,
            running_count=running_count,
            waiting_count=waiting_count,
            token_budget_remaining=token_budget_remaining,
            preempted=preempted,
        )
        self._fh.write(json.dumps(asdict(item), separators=(",", ":")) + "\n")
        self._pending += 1

        if self._pending >= self.flush_every:
            self.flush()

    def flush(self) -> None:
        self._fh.flush()
        self._pending = 0

    def close(self) -> None:
        self.flush()
        self._fh.close()

    def __enter__(self) -> "JsonlRuntimeTrace":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


if __name__ == "__main__":
    with JsonlRuntimeTrace("trace.jsonl") as trace:
        trace.record(
            "scheduler_step",
            iteration_id=1,
            running_count=3,
            waiting_count=2,
            token_budget_remaining=1024,
        )
        trace.record(
            "request_scheduled",
            request_id="req-001",
            iteration_id=1,
            scheduled_tokens=128,
            preempted=False,
        )
