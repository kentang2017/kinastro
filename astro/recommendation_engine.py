"""Shared recommendation framework for dynamic astrology ranking.

This module provides a reusable scoring pipeline for systems that need to rank
many candidates (angels, demons, Aethyrs, remedies, etc.) from natal context.
It supports weighted rules, grouped scoring, profile-based reweighting, and
optional preference overlays while preserving the simple Phase 1 API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterable, Optional, TypeVar

CandidateT = TypeVar("CandidateT")
ContextT = TypeVar("ContextT")


@dataclass(frozen=True)
class CriterionEvaluation:
    """One scoring signal produced by a recommendation rule."""

    score: float
    reason_en: str = ""
    reason_zh: str = ""
    connection_en: str = ""
    connection_zh: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RecommendationRule(Generic[CandidateT, ContextT]):
    """A reusable recommendation rule."""

    key: str
    weight: float
    evaluator: Callable[
        [CandidateT, ContextT],
        Optional[CriterionEvaluation | Iterable[CriterionEvaluation]],
    ]
    group: str = "base"
    enabled: bool = True
    max_contribution: Optional[float] = None


@dataclass(frozen=True)
class RecommendationProfile:
    """Optional weight profile used to reshape scoring for a use case."""

    name: str = "default"
    rule_weights: dict[str, float] = field(default_factory=dict)
    group_weights: dict[str, float] = field(default_factory=dict)
    minimum_score: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class _AccumulatedScore:
    """Internal helper for collecting scoring state for one candidate."""

    raw_score: float = 0.0
    evaluations: list[tuple[str, CriterionEvaluation]] = field(default_factory=list)
    rule_scores: dict[str, float] = field(default_factory=dict)
    group_scores: dict[str, float] = field(default_factory=dict)
    applied_weights: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class RankedCandidate(Generic[CandidateT]):
    """Scored recommendation candidate with score breakdown metadata."""

    item: CandidateT
    raw_score: float
    normalized_score: float
    evaluations: list[tuple[str, CriterionEvaluation]]
    rule_scores: dict[str, float] = field(default_factory=dict)
    group_scores: dict[str, float] = field(default_factory=dict)
    applied_weights: dict[str, float] = field(default_factory=dict)


def _coerce_evaluations(
    result: Optional[CriterionEvaluation | Iterable[CriterionEvaluation]],
) -> list[CriterionEvaluation]:
    """Normalize a rule result into a list of evaluations."""
    if result is None:
        return []
    if isinstance(result, CriterionEvaluation):
        return [result]
    return [item for item in result if item is not None]


def _resolve_effective_weight(
    rule: RecommendationRule[CandidateT, ContextT],
    profile: Optional[RecommendationProfile],
) -> float:
    """Resolve the final multiplier for a rule after profile overrides."""
    effective = float(rule.weight)
    if profile is None:
        return effective
    effective *= float(profile.group_weights.get(rule.group, 1.0))
    effective *= float(profile.rule_weights.get(rule.key, 1.0))
    return effective


def _apply_rule(
    candidate: CandidateT,
    context: ContextT,
    rule: RecommendationRule[CandidateT, ContextT],
    profile: Optional[RecommendationProfile],
    accumulator: _AccumulatedScore,
) -> None:
    """Apply one rule to the current candidate accumulator."""
    if not rule.enabled:
        return

    effective_weight = _resolve_effective_weight(rule, profile)
    accumulator.applied_weights[rule.key] = effective_weight
    if effective_weight == 0:
        return

    evaluations = _coerce_evaluations(rule.evaluator(candidate, context))
    if not evaluations:
        return

    rule_total = 0.0
    for evaluation in evaluations:
        contribution = float(evaluation.score) * effective_weight
        rule_total += contribution
        accumulator.evaluations.append((rule.key, evaluation))

    if rule.max_contribution is not None:
        ceiling = abs(float(rule.max_contribution))
        rule_total = max(-ceiling, min(ceiling, rule_total))

    accumulator.raw_score += rule_total
    accumulator.rule_scores[rule.key] = (
        accumulator.rule_scores.get(rule.key, 0.0) + rule_total
    )
    accumulator.group_scores[rule.group] = (
        accumulator.group_scores.get(rule.group, 0.0) + rule_total
    )


def rank_candidates(  # pylint: disable=too-many-arguments
    candidates: Iterable[CandidateT],
    context: ContextT,
    rules: Iterable[RecommendationRule[CandidateT, ContextT]],
    *,
    top_n: int = 5,
    normalize_score: Optional[Callable[[float], float]] = None,
    profile: Optional[RecommendationProfile] = None,
    preference_rules: Optional[Iterable[RecommendationRule[CandidateT, ContextT]]] = None,
) -> list[RankedCandidate[CandidateT]]:
    """Rank candidates using reusable scoring rules.

    Each rule may emit zero, one, or many :class:`CriterionEvaluation` objects.
    The engine sums ``evaluation.score * effective_weight`` and returns the
    highest-ranked candidates. Effective weight is derived from the rule's base
    weight plus any optional profile/group overrides. Preference rules are just
    additional rules grouped separately so UI or callers can inject user intent
    without rewriting system logic.
    """

    ranked: list[RankedCandidate[CandidateT]] = []
    rules_list = list(rules)
    if preference_rules is not None:
        rules_list.extend(preference_rules)

    for candidate in candidates:
        accumulator = _AccumulatedScore()

        for rule in rules_list:
            _apply_rule(candidate, context, rule, profile, accumulator)

        if profile is not None and profile.minimum_score is not None:
            if accumulator.raw_score < float(profile.minimum_score):
                continue

        normalized = (
            normalize_score(accumulator.raw_score)
            if normalize_score is not None
            else accumulator.raw_score
        )
        ranked.append(
            RankedCandidate(
                item=candidate,
                raw_score=accumulator.raw_score,
                normalized_score=normalized,
                evaluations=accumulator.evaluations,
                rule_scores=accumulator.rule_scores,
                group_scores=accumulator.group_scores,
                applied_weights=accumulator.applied_weights,
            )
        )

    ranked.sort(key=lambda item: item.raw_score, reverse=True)
    return ranked[:top_n]
