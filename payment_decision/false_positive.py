"""False-positive check for one rule against a labeled cohort.

A false positive here is a good event the rule does not allow.
Review and decline both count. Allow does not.
"""

from collections.abc import Callable
from dataclasses import dataclass

from payment_decision.decision import Decision
from payment_decision.event import PaymentEvent

# Illustrative ship bar for this example. Not from any employer.
MAX_FALSE_POSITIVE_RATE = 0.30

LABELS = ("good", "fraud")


@dataclass(frozen=True)
class LabeledEvent:
    """One made-up event plus the label the check scores against."""

    event: PaymentEvent
    label: str

    def __post_init__(self) -> None:
        if self.label not in LABELS:
            raise ValueError("label must be good or fraud")


@dataclass(frozen=True)
class FalsePositiveReport:
    n: int
    n_good: int
    n_fraud: int
    good_not_allowed: int
    false_positive_rate: float
    fraud_not_allowed: int


def false_positive_report(
    labeled_events: list[LabeledEvent],
    decide_fn: Callable[[PaymentEvent], Decision],
) -> FalsePositiveReport:
    """Score one rule. Does not change the events or the rule."""
    if not labeled_events:
        raise ValueError("cohort must contain at least one event")

    n_good = 0
    n_fraud = 0
    good_not_allowed = 0
    fraud_not_allowed = 0
    for labeled in labeled_events:
        not_allowed = decide_fn(labeled.event).action != "allow"
        if labeled.label == "good":
            n_good += 1
            if not_allowed:
                good_not_allowed += 1
        else:
            n_fraud += 1
            if not_allowed:
                fraud_not_allowed += 1

    if n_good == 0:
        raise ValueError("false-positive rate needs at least one good event")

    return FalsePositiveReport(
        n=len(labeled_events),
        n_good=n_good,
        n_fraud=n_fraud,
        good_not_allowed=good_not_allowed,
        false_positive_rate=good_not_allowed / n_good,
        fraud_not_allowed=fraud_not_allowed,
    )


def passes_gate(
    report: FalsePositiveReport,
    max_rate: float = MAX_FALSE_POSITIVE_RATE,
) -> bool:
    """True when the share of good events not allowed is at or under max_rate."""
    if not 0 <= max_rate <= 1:
        raise ValueError("max_rate must be between 0 and 1")
    return report.good_not_allowed <= max_rate * report.n_good
