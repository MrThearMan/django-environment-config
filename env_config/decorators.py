from typing import Any, Callable, Generic, TypeVar

__all__ = [
    "classproperty",
]


R = TypeVar("R")


class classproperty(Generic[R]):  # noqa: N801
    def __init__(self, func: Callable[[type], Any]) -> None:
        self.func = func

    def __get__(self, instance: object, owner: type) -> Any:
        return self.func(owner)
