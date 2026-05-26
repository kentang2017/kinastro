#!/usr/bin/env python3
"""
Generate handler boilerplate for a new astrology system.

Usage:
    python scripts/generate_handler.py --system-id tab_maya --system-name Maya --compute-fn compute_maya_chart --render-fn render_maya_chart

This script creates a new handler file in ui/system_handlers/ with:
- Cached compute wrapper
- Compute function mapping BirthChartParams to compute args
- Render function with AI hook integration
- SystemHandler registration
"""

import argparse
from pathlib import Path


def generate_handler(system_id: str, system_name: str, compute_fn: str, render_fn: str, category: str = "") -> str:
    """Generate handler code for a system."""

    handler_name = system_id.replace("tab_", "build_") + "_handler"
    system_var = system_id.replace("tab_", "")
    category_key = category if category else system_var

    code = f'''"""{system_name} Astrology handler."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def {handler_name}(
    *,
    compute_fn,
    render_fn,
    ai_button_sink,
) -> SystemHandler:
    """Create executable handler for {system_name} Astrology."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], **extra_kwargs):
        """Pure compute wrapped for Streamlit caching."""
        return compute_fn(**params_payload, **extra_kwargs)

    def _compute(params: BirthChartParams, options: dict[str, Any]) -> Any:
        """Compute chart from unified params."""
        payload = params.to_dict()
        # Add system-specific options here if needed
        # e.g., vietnam_mode for ZiWei, ayanamsa for Vedic, etc.
        return _cached_compute(payload)

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        """Render chart with optional AI hook."""
        render_fn(
            result,
            after_chart_hook=lambda: ai_button_sink(
                "{system_id}", result, "{system_var}", ""
            ),
        )

    return SystemHandler(
        system_id="{system_id}",
        compute=_compute,
        render=_render,
        options_schema={{}},  # Add system-specific options here
    )
'''
    return code


def main():
    parser = argparse.ArgumentParser(description="Generate handler boilerplate")
    parser.add_argument("--system-id", required=True, help="System tab ID (e.g., tab_maya)")
    parser.add_argument("--system-name", required=True, help="System name (e.g., Maya)")
    parser.add_argument("--compute-fn", required=True, help="Compute function name")
    parser.add_argument("--render-fn", required=True, help="Render function name")
    parser.add_argument("--category", default="", help="Category key (optional)")
    parser.add_argument("--output", "-o", help="Output file path (optional, defaults to ui/system_handlers/)")

    args = parser.parse_args()

    code = generate_handler(
        system_id=args.system_id,
        system_name=args.system_name,
        compute_fn=args.compute_fn,
        render_fn=args.render_fn,
        category=args.category,
    )

    output_path = args.output
    if not output_path:
        output_dir = Path("ui/system_handlers")
        output_dir.mkdir(exist_ok=True)
        handler_filename = f"build_{args.system_id.replace('tab_', '')}_handler.py"
        output_path = output_dir / handler_filename

    Path(output_path).write_text(code, encoding="utf-8")
    print(f"Generated handler: {output_path}")


if __name__ == "__main__":
    main()
