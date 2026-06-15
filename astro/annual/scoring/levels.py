"""Score to fortune-level mapping."""

from __future__ import annotations

from astro.annual.models import FortuneLevel


def score_to_level(score: float) -> FortuneLevel:
    if score >= 80:
        return FortuneLevel.EXCELLENT
    if score >= 65:
        return FortuneLevel.GOOD
    if score >= 45:
        return FortuneLevel.NEUTRAL
    if score >= 30:
        return FortuneLevel.CAUTION
    return FortuneLevel.CRITICAL


def clamp_score(score: float) -> float:
    return max(0.0, min(100.0, float(score)))