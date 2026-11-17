"""Per-request metrics: tokens, tool calls, latency, tokens/sec, cost-per-request.

ADK callbacks write into a ContextVar, so metrics follow one request even when
sub-agents run as tools.
"""
from __future__ import annotations

import logging
from contextvars import ContextVar
from dataclasses import dataclass, field

from oracle.config import get_settings

log = logging.getLogger("oracle")


@dataclass
class RequestMetrics:
    input_tokens: int = 0
    output_tokens: int = 0
    llm_calls: int = 0
    tool_calls: list[str] = field(default_factory=list)

    def to_dict(self, latency_ms: float) -> dict:
        cfg = get_settings()
        cost = (
            self.input_tokens * cfg.price_per_1m_input
            + self.output_tokens * cfg.price_per_1m_output
        ) / 1_000_000
        seconds = max(latency_ms / 1000, 1e-9)
        return {
            "latency_ms": round(latency_ms, 1),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "llm_calls": self.llm_calls,
            "tool_calls": list(self.tool_calls),
            "tokens_per_sec": round(self.output_tokens / seconds, 2),
            "cost_usd": round(cost, 6),
        }


_current: ContextVar[RequestMetrics | None] = ContextVar("oracle_metrics", default=None)


def start_request() -> RequestMetrics:
    metrics = RequestMetrics()
    _current.set(metrics)
    return metrics


def after_model_callback(callback_context, llm_response):
    """Count tokens after every LLM call. Returning nothing keeps the response unchanged."""
    metrics = _current.get()
    usage = getattr(llm_response, "usage_metadata", None)
    if metrics is not None and usage is not None:
        metrics.input_tokens += getattr(usage, "prompt_token_count", 0) or 0
        metrics.output_tokens += getattr(usage, "candidates_token_count", 0) or 0
        metrics.llm_calls += 1


def before_tool_callback(tool, args, tool_context):
    """Log every tool call (including sub-agents invoked as tools)."""
    metrics = _current.get()
    if metrics is not None:
        metrics.tool_calls.append(tool.name)
    log.info("tool_call name=%s", tool.name)


CALLBACKS = {
    "after_model_callback": after_model_callback,
    "before_tool_callback": before_tool_callback,
}
