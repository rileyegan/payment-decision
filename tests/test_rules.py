"""Each example reason, plus proof that the first matching rule wins."""

import pytest

from payment_decision.event import PaymentEvent
from payment_decision.rules import decide


def event(**overrides) -> PaymentEvent:
    fields = {
        "amount_cents": 1_000,
        "account_age_days": 100,
        "declines_in_last_hour": 0,
        "country_mismatch": False,
        "merchant_category": "grocery",
    }
    fields.update(overrides)
    return PaymentEvent(**fields)


def test_velocity_declines() -> None:
    decision = decide(event(declines_in_last_hour=3))
    assert decision.action == "decline"
    assert decision.reason_code == "velocity_declines"


def test_new_account_high_amount_country_mismatch() -> None:
    decision = decide(
        event(amount_cents=50_000, account_age_days=6, country_mismatch=True)
    )
    assert decision.action == "decline"
    assert decision.reason_code == "new_account_high_amount_country_mismatch"


def test_new_account_elevated_amount() -> None:
    decision = decide(event(amount_cents=20_000, account_age_days=6))
    assert decision.action == "review"
    assert decision.reason_code == "new_account_elevated_amount"


def test_within_policy() -> None:
    decision = decide(event())
    assert decision.action == "allow"
    assert decision.reason_code == "within_policy"


def test_first_matching_rule_wins() -> None:
    # This event also matches the high-amount decline and the elevated review.
    # Velocity is first, so those later rules do not run.
    decision = decide(
        event(
            amount_cents=80_000,
            account_age_days=1,
            declines_in_last_hour=3,
            country_mismatch=True,
        )
    )
    assert decision.reason_code == "velocity_declines"


def test_day_seven_is_not_a_new_account() -> None:
    decision = decide(
        event(amount_cents=50_000, account_age_days=7, country_mismatch=True)
    )
    assert decision.reason_code == "within_policy"


def test_amount_just_under_high_cutoff_is_review() -> None:
    decision = decide(
        event(amount_cents=49_999, account_age_days=6, country_mismatch=True)
    )
    assert decision.reason_code == "new_account_elevated_amount"


def test_amount_just_under_elevated_cutoff_is_allow() -> None:
    decision = decide(event(amount_cents=19_999, account_age_days=6))
    assert decision.reason_code == "within_policy"


def test_two_declines_do_not_trip_velocity() -> None:
    decision = decide(event(declines_in_last_hour=2))
    assert decision.reason_code == "within_policy"


def test_merchant_category_does_not_change_the_decision() -> None:
    grocery = decide(event(merchant_category="grocery"))
    money = decide(event(merchant_category="money_movement"))
    assert grocery == money


def test_bad_event_is_rejected() -> None:
    with pytest.raises(ValueError):
        event(amount_cents=-1)
    with pytest.raises(ValueError):
        event(merchant_category="acme")
