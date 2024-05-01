from __future__ import annotations

from typing import TYPE_CHECKING

from env_config.constants import Undefined

if TYPE_CHECKING:
    from env_config import Environment


__all__ = [
    "DjangoEnvConfigError",
    "MissingEnvValueError",
    "MissingExtraDependencyError",
]


class DjangoEnvConfigError(Exception):
    """Base class for all Django Environment Config errors."""


class MissingEnvValueError(DjangoEnvConfigError):
    """Error raised when a value is not found in the .env file, and a default is not provided."""

    def __init__(self, *, name: str, env: type[Environment]) -> None:
        msg = f"Value {name!r} in environment {env.__name__!r}"
        if env.dotenv_path is not Undefined:
            msg += " not defined in the .env file and value does not have a default"
        else:
            msg += " needs a default value since environment does not define a `dotenv_path`"

        super().__init__(msg)


class MissingExtraDependencyError(DjangoEnvConfigError):
    """Base class for all Django Environment Config errors."""
