"""Print one JSON decision for a synthetic payment event.

Reads flags only. Does not open a file, call the network, or write a decision anywhere.
"""

import argparse
import json
import sys

from payment_decision.event import MERCHANT_CATEGORIES, PaymentEvent
from payment_decision.rules import decide


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Decide one made-up payment event and print the reason."
    )
    parser.add_argument("--amount-cents", type=int, required=True)
    parser.add_argument("--account-age-days", type=int, required=True)
    parser.add_argument("--declines-in-last-hour", type=int, required=True)
    # Absent flag means no mismatch. The flag stores true; it does not take a value.
    parser.add_argument("--country-mismatch", action="store_true")
    parser.add_argument(
        "--merchant-category",
        default="grocery",
        choices=MERCHANT_CATEGORIES,
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        event = PaymentEvent(
            amount_cents=args.amount_cents,
            account_age_days=args.account_age_days,
            declines_in_last_hour=args.declines_in_last_hour,
            country_mismatch=args.country_mismatch,
            merchant_category=args.merchant_category,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    # Print the decision only. Leaves the working tree unchanged.
    print(json.dumps(decide(event).as_dict()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
