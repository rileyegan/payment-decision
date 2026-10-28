"""Example payment rules.

The cutoffs below are made up so the tests have stable numbers.
They are not copied from an employer, and they are not a merchant list.
"""

from payment_decision.decision import Decision
from payment_decision.event import PaymentEvent

# Illustrative cutoffs for this example. Not from any employer.
VELOCITY_DECLINE_AT = 3
NEW_ACCOUNT_DAYS = 7
HIGH_AMOUNT_CENTS = 50_000
ELEVATED_AMOUNT_CENTS = 20_000
BROAD_NEW_ACCOUNT_DAYS = 30


def decide(event: PaymentEvent) -> Decision:
    """Apply the example rules in order. The first match is the decision.

    A review is not an allow. The false-positive check treats both review
    and decline as "not allowed."
    """
    if event.declines_in_last_hour >= VELOCITY_DECLINE_AT:
        return Decision(
            action="decline",
            reason_code="velocity_declines",
            reason="Three or more declines in the last hour.",
        )
    if (
        event.account_age_days < NEW_ACCOUNT_DAYS
        and event.amount_cents >= HIGH_AMOUNT_CENTS
        and event.country_mismatch
    ):
        return Decision(
            action="decline",
            reason_code="new_account_high_amount_country_mismatch",
            reason="New account, high amount, and country mismatch.",
        )
    if (
        event.account_age_days < NEW_ACCOUNT_DAYS
        and event.amount_cents >= ELEVATED_AMOUNT_CENTS
    ):
        return Decision(
            action="review",
            reason_code="new_account_elevated_amount",
            reason="New account and elevated amount.",
        )
    return Decision(
        action="allow",
        reason_code="within_policy",
        reason="No example rule matched.",
    )


def decline_every_new_account(event: PaymentEvent) -> Decision:
    """Over-broad rule. Declines every account under 30 days.

    The sample cohort uses this to show a rule that fails the false-positive gate.
    It is not a rule to ship.
    """
    if event.account_age_days < BROAD_NEW_ACCOUNT_DAYS:
        return Decision(
            action="decline",
            reason_code="broad_new_account",
            reason="Account is under 30 days.",
        )
    return Decision(
        action="allow",
        reason_code="within_policy",
        reason="Account is 30 days or older.",
    )
