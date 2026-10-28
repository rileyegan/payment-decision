"""Hand-written cohort. Counts below are the expected false-positive check.

Good events (8). `decide` does not allow 2 of them (1 review, 1 decline).
False-positive rate = 2/8 = 0.25, which is under the 0.30 example gate.

The same 8 good events: 5 are under 30 days, so `decline_every_new_account`
does not allow 5/8 = 0.625 and fails the same gate.

Fraud events are in the cohort so a miss is visible. They do not enter the rate.
"""

import json
import subprocess
import sys

import pytest

from payment_decision.event import PaymentEvent
from payment_decision.false_positive import (
    LabeledEvent,
    false_positive_report,
    passes_gate,
)
from payment_decision.rules import decide, decline_every_new_account


def labeled(
    amount_cents: int,
    account_age_days: int,
    declines_in_last_hour: int,
    country_mismatch: bool,
    merchant_category: str,
    label: str,
) -> LabeledEvent:
    return LabeledEvent(
        PaymentEvent(
            amount_cents=amount_cents,
            account_age_days=account_age_days,
            declines_in_last_hour=declines_in_last_hour,
            country_mismatch=country_mismatch,
            merchant_category=merchant_category,
        ),
        label,
    )


# Made-up rows. The trailing comment is the `decide` result, not a stored label.
COHORT = [
    labeled(15_000, 100, 0, False, "grocery", "good"),  # allow
    labeled(8_000, 40, 0, False, "digital_goods", "good"),  # allow
    labeled(5_000, 20, 1, False, "grocery", "good"),  # allow
    labeled(10_000, 10, 0, False, "money_movement", "good"),  # allow
    labeled(40_000, 90, 0, True, "grocery", "good"),  # allow
    labeled(19_000, 8, 2, False, "digital_goods", "good"),  # allow
    labeled(25_000, 3, 0, False, "grocery", "good"),  # review
    labeled(60_000, 1, 0, True, "digital_goods", "good"),  # decline
    labeled(80_000, 2, 0, True, "money_movement", "fraud"),  # decline
    labeled(30_000, 1, 0, False, "grocery", "fraud"),  # review
    labeled(10_000, 4, 5, False, "digital_goods", "fraud"),  # decline
    labeled(5_000, 60, 4, False, "grocery", "fraud"),  # decline
    labeled(3_000, 200, 0, False, "grocery", "fraud"),  # allow
]


def test_balanced_rule_passes_gate() -> None:
    report = false_positive_report(COHORT, decide)
    assert report.n == 13
    assert report.n_good == 8
    assert report.n_fraud == 5
    assert report.good_not_allowed == 2
    assert report.false_positive_rate == 0.25
    assert report.fraud_not_allowed == 4
    assert passes_gate(report) is True


def test_over_broad_rule_fails_same_gate() -> None:
    report = false_positive_report(COHORT, decline_every_new_account)
    assert report.n_good == 8
    assert report.good_not_allowed == 5
    assert report.false_positive_rate == 0.625
    assert passes_gate(report) is False


def test_review_counts_as_not_allowed() -> None:
    one_good_review = [labeled(25_000, 3, 0, False, "grocery", "good")]
    report = false_positive_report(one_good_review, decide)
    assert report.good_not_allowed == 1
    assert passes_gate(report, max_rate=0.0) is False


def test_gate_bounds() -> None:
    report = false_positive_report(COHORT, decide)
    with pytest.raises(ValueError):
        passes_gate(report, max_rate=1.1)
    with pytest.raises(ValueError):
        passes_gate(report, max_rate=-0.01)


def test_cohort_must_include_a_good_event() -> None:
    fraud_only = [labeled(3_000, 200, 0, False, "grocery", "fraud")]
    with pytest.raises(ValueError):
        false_positive_report(fraud_only, decide)
    with pytest.raises(ValueError):
        false_positive_report([], decide)
    with pytest.raises(ValueError):
        LabeledEvent(
            PaymentEvent(1_000, 10, 0, False, "grocery"),
            "unknown",
        )


def test_cli_prints_one_decision() -> None:
    # Same flags as the README. Expect review, because $250 on a 3-day account
    # is under the high-amount decline and over the elevated-amount review.
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "payment_decision",
            "--amount-cents",
            "25000",
            "--account-age-days",
            "3",
            "--declines-in-last-hour",
            "0",
            "--country-mismatch",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(completed.stdout) == {
        "action": "review",
        "reason_code": "new_account_elevated_amount",
        "reason": "New account and elevated amount.",
    }
    assert completed.stderr == ""
