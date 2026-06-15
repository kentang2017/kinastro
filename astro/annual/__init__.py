"""Solar-return annual multi-system flow timeline."""

from astro.annual.models import (
    AnnualFlowYear,
    LiurenJixiong,
    SolarReturnTimeline,
    SolarReturnTimelineRequest,
)
from astro.annual.cache import clear_annual_timeline_cache, compute_annual_timeline_cached
from astro.annual.timeline import compute_solar_return_flowyear_timeline

try:
    from astro.annual.render import generate_annual_sr_pdf, render_annual_sr_timeline_panel
except ImportError:  # pragma: no cover - optional UI stack
    generate_annual_sr_pdf = None
    render_annual_sr_timeline_panel = None

__all__ = [
    "AnnualFlowYear",
    "LiurenJixiong",
    "SolarReturnTimeline",
    "SolarReturnTimelineRequest",
    "compute_solar_return_flowyear_timeline",
    "compute_annual_timeline_cached",
    "clear_annual_timeline_cache",
    "generate_annual_sr_pdf",
    "render_annual_sr_timeline_panel",
]