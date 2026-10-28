"""The result a caller gets back: an action, a reason code, and a short reason."""

from dataclasses import dataclass
from typing import Literal

Action = Literal["allow", "review", "decline"]
ACTIONS = ("allow", "review", "decline")


@dataclass(frozen=True)
class Decision:
    action: Action
    reason_code: str
    reason: str

    def __post_init__(self) -> None:
        if self.action not in ACTIONS:
            raise ValueError("action must be allow, review, or decline")
        if not self.reason_code or not self.reason:
            raise ValueError("reason_code and reason must be non-empty")

    def as_dict(self) -> dict[str, str]:
        """Plain dict for JSON printing. Same three fields, no extras."""
        return {
            "action": self.action,
            "reason_code": self.reason_code,
            "reason": self.reason,
        }
