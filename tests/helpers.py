from __future__ import annotations

from functools import wraps
from unittest.mock import patch

from env_config.typing import Any, Callable, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


class set_dotenv:
    def __init__(self, **values: Any) -> None:
        self.patch = patch("env_config.base.dotenv_values", return_value=values)

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Run the test with the method patched
            with self.patch:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        return self.patch.__enter__()

    def __exit__(self, *args):
        return self.patch.__exit__(*args)
