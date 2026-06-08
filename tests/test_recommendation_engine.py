"""Focused tests for the shared recommendation engine."""

from __future__ import annotations

from dataclasses import dataclass

from astro.recommendation_engine import (
    CriterionEvaluation,
    RecommendationProfile,
    RecommendationRule,
    rank_candidates,
)


@dataclass(frozen=True)
class Candidate:
    """Simple candidate used for engine tests."""

    name: str
    affinity: float


@dataclass(frozen=True)
class Context:
    """Simple context used for engine tests."""

    boost: float


def test_rank_candidates_applies_profile_group_and_rule_weights() -> None:
    """Profile overrides should reshape final scores."""
    candidates = [Candidate("A", 1.0), Candidate("B", 0.5)]

    ranked = rank_candidates(
        candidates,
        Context(boost=1.0),
        rules=[
            RecommendationRule(
                "affinity",
                1.0,
                lambda candidate, _: CriterionEvaluation(score=candidate.affinity),
                group="planetary",
            ),
            RecommendationRule(
                "boost",
                1.0,
                lambda _, context: CriterionEvaluation(score=context.boost),
                group="preference",
            ),
        ],
        profile=RecommendationProfile(
            name="weighted",
            rule_weights={"affinity": 2.0},
            group_weights={"planetary": 1.5, "preference": 0.5},
        ),
    )

    assert [item.item.name for item in ranked] == ["A", "B"]
    assert ranked[0].rule_scores["affinity"] == 3.0
    assert ranked[0].rule_scores["boost"] == 0.5
    assert ranked[0].group_scores["planetary"] == 3.0
    assert ranked[0].group_scores["preference"] == 0.5


def test_rank_candidates_accepts_preference_rules() -> None:
    """Preference rules should behave like an additive overlay."""
    ranked = rank_candidates(
        [Candidate("A", 0.4), Candidate("B", 0.6)],
        Context(boost=1.0),
        rules=[
            RecommendationRule(
                "base",
                1.0,
                lambda candidate, _: CriterionEvaluation(score=candidate.affinity),
            ),
        ],
        preference_rules=[
            RecommendationRule(
                "user_preference",
                1.0,
                lambda candidate, context: (
                    CriterionEvaluation(score=context.boost)
                    if candidate.name == "A"
                    else None
                ),
                group="preference",
            ),
        ],
    )

    assert [item.item.name for item in ranked] == ["A", "B"]
    assert ranked[0].rule_scores["user_preference"] == 1.0
    assert ranked[0].raw_score == 1.4
    assert ranked[1].raw_score == 0.6


def test_rank_candidates_respects_rule_max_contribution() -> None:
    """A rule cap should prevent one signal from dominating the result."""
    ranked = rank_candidates(
        [Candidate("A", 10.0)],
        Context(boost=0.0),
        rules=[
            RecommendationRule(
                "capped",
                1.0,
                lambda candidate, _: CriterionEvaluation(score=candidate.affinity),
                max_contribution=2.5,
            ),
        ],
    )

    assert ranked[0].raw_score == 2.5
