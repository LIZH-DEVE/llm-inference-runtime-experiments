#!/usr/bin/env python3
"""Summarize request-correlated scheduler trace JSONL."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(ordered[lo])
    frac = pos - lo
    return float(ordered[lo] * (1.0 - frac) + ordered[hi] * frac)


def summarize(values: list[float]) -> str:
    if not values:
        return "n=0"
    return (
        f"n={len(values)} "
        f"median={statistics.median(values):.2f} "
        f"p95={percentile(values, 0.95):.2f} "
        f"max={max(values):.2f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()

    scheduler_steps = []
    scheduled_events = []
    preemptions = []
    first_schedule: dict[str, int] = {}
    tokens_per_request: dict[str, int] = defaultdict(int)

    with args.trace.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            event = row.get("event")

            if event == "scheduler_step":
                scheduler_steps.append(row)
            elif event == "request_scheduled":
                scheduled_events.append(row)
                request_id = row.get("request_id")
                iteration_id = row.get("iteration_id")
                if request_id is not None and iteration_id is not None:
                    first_schedule.setdefault(str(request_id), int(iteration_id))
                    tokens_per_request[str(request_id)] += int(
                        row.get("scheduled_tokens") or 0
                    )
                if row.get("preempted"):
                    preemptions.append(row)
            elif event == "request_preempted":
                preemptions.append(row)

    running = [
        float(row["running_count"])
        for row in scheduler_steps
        if row.get("running_count") is not None
    ]
    waiting = [
        float(row["waiting_count"])
        for row in scheduler_steps
        if row.get("waiting_count") is not None
    ]
    scheduled_tokens = [
        float(row["scheduled_tokens"])
        for row in scheduled_events
        if row.get("scheduled_tokens") is not None
    ]

    print(f"scheduler_steps={len(scheduler_steps)}")
    print(f"request_schedule_events={len(scheduled_events)}")
    print(f"unique_requests={len(first_schedule)}")
    print(f"preemption_events={len(preemptions)}")
    print(f"running_count: {summarize(running)}")
    print(f"waiting_count: {summarize(waiting)}")
    print(f"scheduled_tokens: {summarize(scheduled_tokens)}")

    if first_schedule:
        first_values = [float(v) for v in first_schedule.values()]
        print(f"first_schedule_iteration: {summarize(first_values)}")

    if tokens_per_request:
        totals = [float(v) for v in tokens_per_request.values()]
        print(f"scheduled_tokens_per_request: {summarize(totals)}")


if __name__ == "__main__":
    main()
