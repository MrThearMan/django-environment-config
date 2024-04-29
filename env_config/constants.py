from __future__ import annotations

__all__ = [
    "ENV_NAME",
    "Undefined",
]


class Undefined:  # pragma: no cover
    """Value to represent an undefined value."""

    def __repr__(self) -> str:
        return self.__class__.__name__

    def __bool__(self) -> bool:
        return False


Undefined = Undefined()

ENV_NAME = "DJANGO_SETTINGS_ENVIRONMENT"
