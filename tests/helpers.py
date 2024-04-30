from __future__ import annotations

import os
from functools import wraps
from unittest.mock import patch

from env_config import Environment
from env_config.typing import Any, Callable, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


__all__ = [
    "set_dotenv",
    "set_environ",
]


class set_dotenv:
    def __init__(self, env: str, /, **values: Any) -> None:
        self.env = env
        path = Environment.load_dotenv.__module__ + "." + Environment.load_dotenv.__qualname__
        self.patch = patch(path, return_value=values)

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Run the test with the method patched
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        os.environ["DJANGO_SETTINGS_ENVIRONMENT"] = self.env
        return self.patch.__enter__()

    def __exit__(self, *args):
        os.environ.pop("DJANGO_SETTINGS_ENVIRONMENT", None)
        return self.patch.__exit__(*args)


class set_environ:
    def __init__(self, env: str, /, **values: Any) -> None:
        self.env = env
        self.values = values

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Run the test with the method patched
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        os.environ["DJANGO_SETTINGS_ENVIRONMENT"] = self.env
        os.environ.update(self.values)

    def __exit__(self, *args):
        os.environ.pop("DJANGO_SETTINGS_ENVIRONMENT", None)
        for value in self.values:
            os.environ.pop(value, None)
