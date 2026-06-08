"""Shared recommendation framework for dynamic astrology ranking.

Provides a small, extensible engine for systems that need to score many
candidates (angels, demons, Aethyrs, remedies, etc.) from natal context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, Optional, TypeVar

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
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RecommendationRule(Generic[CandidateT, ContextT]):
    """A reusable recommendation rule."""

    key: str
    weight: float
    evaluator: Callable[
        [CandidateT, ContextT],
        Optional[CriterionEvaluation | Iterable[CriterionEvaluation]],
    ]


@dataclass(frozen=True)
class RankedCandidate(Generic[CandidateT]):
    """Scored recommendation candidate."""

    item: CandidateT
    raw_score: float
    normalized_score: float
    evaluations: list[tuple[str, CriterionEvaluation]]


def rank_candidates(
    candidates: Iterable[CandidateT],
    context: ContextT,
    rules: Iterable[RecommendationRule[CandidateT, ContextT]],
    *,
    top_n: int = 5,
    normalize_score: Optional[Callable[[float], float]] = None,
) -> list[RankedCandidate[CandidateT]]:
    """Rank candidates using reusable scoring rules.

    Each rule may emit zero, one, or many `CriterionEvaluation` objects. The
    engine sums `evaluation.score * rule.weight` and returns the highest-ranked
    candidates. Normalization is caller-controlled so each astrology system can
    preserve its own semantics.
    """

    ranked: list[RankedCandidate[CandidateT]] = []
    rules_list = list(rules)

    for candidate in candidates:
        raw_score = 0.0
        matched: list[tuple[str, CriterionEvaluation]] = []
        for rule in rules_list:
            result = rule.evaluator(candidate, context)
            if result is None:
                continue
            if isinstance(result, CriterionEvaluation):
                evaluations = [result]
            else:
                evaluations = [item for item in result if item is not None]
            for evaluation in evaluations:
                raw_score += float(evaluation.score) * float(rule.weight)
                matched.append((rule.key, evaluation))

        normalized = (
            normalize_score(raw_score)
            if normalize_score is not None
            else raw_score
        )
        ranked.append(
            RankedCandidate(
                item=candidate,
                raw_score=raw_score,
                normalized_score=normalized,
                evaluations=matched,
            )
        )

    ranked.sort(key=lambda item: item.raw_score, reverse=True)
    return ranked[:top_n]
