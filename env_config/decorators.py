from collections.abc import Callable
from typing import Any

__all__ = [
    "classproperty",
]


class classproperty[R]:  # noqa: N801
    def __init__(self, func: Callable[[type], Any]) -> None:
        self.func = func

    def __get__(self, instance: object, owner: type) -> Any:
        return self.func(owner)
