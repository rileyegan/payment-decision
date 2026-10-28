"""One synthetic card-not-present payment. No account id, card number, or email."""

from dataclasses import dataclass

MERCHANT_CATEGORIES = ("grocery", "digital_goods", "money_movement")


@dataclass(frozen=True)
class PaymentEvent:
    """Fields a recruiter can read. Categories are labels for this example only."""

    amount_cents: int
    account_age_days: int
    declines_in_last_hour: int
    country_mismatch: bool
    merchant_category: str

    def __post_init__(self) -> None:
        # Reject bad fixture data before a rule can treat it as a real signal.
        # These checks do not look up a person, a card, or a merchant list.
        if self.amount_cents < 0:
            raise ValueError("amount_cents must be zero or greater")
        if self.account_age_days < 0:
            raise ValueError("account_age_days must be zero or greater")
        if self.declines_in_last_hour < 0:
            raise ValueError("declines_in_last_hour must be zero or greater")
        if self.merchant_category not in MERCHANT_CATEGORIES:
            raise ValueError(
                "merchant_category must be grocery, digital_goods, or money_movement"
            )
