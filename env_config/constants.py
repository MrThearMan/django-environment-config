from __future__ import annotations

from enum import Enum
from typing import Final, Literal

__all__ = [
    "ENV_NAME",
    "Undefined",
    "UndefinedType",
]


class UndefinedType(Enum):
    """Value to represent an undefined value."""

    # A single-member enum is a sentinel that type checkers can narrow with `is` checks.
    Undefined = "Undefined"

    def __repr__(self) -> str:
        return self.value

    def __bool__(self) -> Literal[False]:
        return False


Undefined: Final = UndefinedType.Undefined

ENV_NAME = "DJANGO_SETTINGS_ENVIRONMENT"
