#!/usr/bin/env python3
"""Request-correlated scheduler tracing for vLLM V1.

The adapter wraps Scheduler.schedule() and records scheduler-level events without
serializing full Request objects. It targets the vLLM 0.26.x V1 scheduler API.
Install the wrapper before constructing the LLM engine.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from instrumentation.request_correlated_trace import JsonlRuntimeTrace


def install_scheduler_trace(
    trace: JsonlRuntimeTrace,
) -> Callable[..., Any]:
    from vllm.v1.core.sched.scheduler import Scheduler

    if getattr(Scheduler, "_runtime_trace_installed", False):
        raise RuntimeError("scheduler trace is already installed")

    original_schedule = Scheduler.schedule

    def traced_schedule(self, *args, **kwargs):
        output = original_schedule(self, *args, **kwargs)

        iteration_id = getattr(self, "current_step", None)
        running_count = len(self.running)
        waiting_count = len(self.waiting)
        max_tokens = int(getattr(self, "max_num_scheduled_tokens", 0))
        total_tokens = int(output.total_num_scheduled_tokens)
        token_budget_remaining = max(max_tokens - total_tokens, 0)

        trace.record(
            "scheduler_step",
            iteration_id=iteration_id,
            running_count=running_count,
            waiting_count=waiting_count,
            token_budget_remaining=token_budget_remaining,
        )

        preempted = set(output.preempted_req_ids or ())
        for request_id, scheduled_tokens in output.num_scheduled_tokens.items():
            trace.record(
                "request_scheduled",
                request_id=request_id,
                iteration_id=iteration_id,
                scheduled_tokens=int(scheduled_tokens),
                running_count=running_count,
                waiting_count=waiting_count,
                token_budget_remaining=token_budget_remaining,
                preempted=request_id in preempted,
            )

        for request_id in sorted(preempted):
            if request_id not in output.num_scheduled_tokens:
                trace.record(
                    "request_preempted",
                    request_id=request_id,
                    iteration_id=iteration_id,
                    running_count=running_count,
                    waiting_count=waiting_count,
                    token_budget_remaining=token_budget_remaining,
                    preempted=True,
                )

        return output

    Scheduler.schedule = traced_schedule
    Scheduler._runtime_trace_installed = True
    return original_schedule


def uninstall_scheduler_trace(original_schedule: Callable[..., Any]) -> None:
    from vllm.v1.core.sched.scheduler import Scheduler

    Scheduler.schedule = original_schedule
    Scheduler._runtime_trace_installed = False
