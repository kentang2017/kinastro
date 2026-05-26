"""Runtime system registry with lazy imports and cached compute orchestration."""

from __future__ import annotations

import importlib
import json
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Callable

import streamlit as st

from ui.components.birth_form import BirthChartParams


ComputeCallable = Callable[[dict[str, Any], dict[str, Any]], Any]
RenderCallable = Callable[[Any, BirthChartParams, dict[str, Any], Callable[[], None] | None], None]


@dataclass(frozen=True)
class SystemSpec:
    compute: str
    render: str
    import_path: str


SYSTEM_REGISTRY: dict[str, SystemSpec] = {
    "tab_western": SystemSpec(
        compute="systems.western.calculator:compute",
        render="systems.western.renderer:render",
        import_path="systems.western",
    ),
    "tab_ziwei": SystemSpec(
        compute="systems.ziwei.calculator:compute",
        render="systems.ziwei.renderer:render",
        import_path="systems.ziwei",
    ),
    "tab_indian": SystemSpec(
        compute="systems.vedic.calculator:compute",
        render="systems.vedic.renderer:render",
        import_path="systems.vedic",
    ),
}

_RUNTIME_CACHE: dict[str, tuple[ComputeCallable, RenderCallable]] = {}


def _load_attr(path: str) -> Any:
    module_name, attr = path.split(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


def _load_runtime(system_name: str) -> tuple[ComputeCallable, RenderCallable]:
    cached = _RUNTIME_CACHE.get(system_name)
    if cached is not None:
        return cached
    spec = SYSTEM_REGISTRY[system_name]
    compute = _load_attr(spec.compute)
    render = _load_attr(spec.render)
    pair = (compute, render)
    _RUNTIME_CACHE[system_name] = pair
    return pair


def _stable_digest(params_payload: dict[str, Any], options: dict[str, Any]) -> str:
    packed = json.dumps({"params": params_payload, "options": options}, sort_keys=True)
    return sha256(packed.encode("utf-8")).hexdigest()


@st.cache_data(ttl=3600, show_spinner=False)
def _compute_cached(system_name: str, payload_json: str, options_json: str) -> Any:
    payload = json.loads(payload_json)
    options = json.loads(options_json)
    compute, _ = _load_runtime(system_name)
    return compute(payload, options)


def get_or_compute(system_name: str, birth_params: BirthChartParams, options: dict[str, Any] | None = None) -> dict[str, Any]:
    opts = options or {}
    # BirthChartParams.to_dict intentionally excludes gender for legacy compatibility.
    payload = {**birth_params.to_dict(), "gender": birth_params.gender}
    signature = _stable_digest(payload, opts)

    chart_cache = st.session_state.setdefault("charts", {})
    metrics = st.session_state.setdefault(
        "perf_metrics",
        {"hits": 0, "misses": 0, "last_compute_seconds": 0.0},
    )

    cached = chart_cache.get(system_name)
    if cached and cached.get("signature") == signature:
        metrics["hits"] += 1
        return {"result": cached["result"], "from_cache": True, "duration": 0.0, "signature": signature}

    metrics["misses"] += 1
    start = time.perf_counter()
    result = _compute_cached(
        system_name,
        json.dumps(payload, sort_keys=True),
        json.dumps(opts, sort_keys=True),
    )
    duration = time.perf_counter() - start
    metrics["last_compute_seconds"] = duration
    chart_cache[system_name] = {"signature": signature, "result": result}
    return {"result": result, "from_cache": False, "duration": duration, "signature": signature}


def render_system(
    system_name: str,
    chart_result: Any,
    birth_params: BirthChartParams,
    options: dict[str, Any] | None = None,
    ai_hook: Callable[[], None] | None = None,
) -> None:
    opts = options or {}
    _, render = _load_runtime(system_name)
    render(chart_result, birth_params, opts, ai_hook)


def supports_modern_runtime(system_name: str | None) -> bool:
    return bool(system_name) and system_name in SYSTEM_REGISTRY
