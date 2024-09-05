from __future__ import annotations

import inspect
import os
from typing import TYPE_CHECKING

from django.utils.functional import classproperty
from dotenv import dotenv_values
from dotenv.main import find_dotenv

from .constants import ENV_NAME, Undefined

if TYPE_CHECKING:
    from dotenv.main import StrPath

    from .typing import Any

__all__ = [
    "Environment",
]


class Environment:
    """
    Configures a single environment.

    Creation of a subclasses can be customized by setting keyword arguments on the class.
    See `__init_subclass__` for more info.

    >>> class MyEnvironment(Environment, use_environ=True):
    >>>     pass
    """

    def __init_subclass__(
        cls,
        *,
        dotenv_path: StrPath | None | Undefined = Undefined,
        use_environ: bool = False,
        overrides_from: type | None = None,
    ) -> None:
        """
        When a subclass of environment is created, try to immediately load the settings
        and set them in the module globals where the environment is defined, if the environment matches
        what has been selected with the `DJANGO_SETTINGS_ENVIRONMENT` environment variable.

        :param dotenv_path: The path to the `.env` file to load. If set to `None`, the `.env` file will not be loaded.
                            By default, `python-dotenv` will try to find the `.env` file automatically.
        :param use_environ: If set to `True`, use environment variables instead of using a `.env` file.
        :param overrides_from: If set, the values from this class will be used as overrides for the values in the
                               environment.
        """
        if overrides_from is not None:
            for name, value in overrides_from.__dict__.items():
                if name.isupper() and not name.startswith("_"):
                    setattr(cls, name, value)

        env: str | None = os.environ.get(ENV_NAME)
        if env is None:  # pragma: no cover
            msg = f"Environment variable {ENV_NAME!r} must be set before subclassing 'Environment'"
            raise ValueError(msg)

        # If the environment does not match, do not load the environment or even the `.env` file.
        if cls.__name__.casefold() != env.casefold():
            return

        # If set to `None` explicitly, or using environment, do not load a `.env` file.
        if dotenv_path is None or use_environ:
            dotenv_path = Undefined

        # If not given, set it to `None` so the `dotenv.main.find_dotenv`
        # will try to find the `.env` file automatically.
        elif dotenv_path is Undefined:
            dotenv_path = None

        dotenv: dict[str, str] | Undefined
        if use_environ:
            dotenv = os.environ.copy()
        elif dotenv_path is not Undefined:
            dotenv = cls.load_dotenv(dotenv_path=dotenv_path)
        else:
            dotenv = Undefined

        # Do name mangling to avoid overriding the attribute from a parent class.
        # This way, we can have multiple environments with different `.env` files,
        # and allow using values from a parent `.env` file as defaults (if desired).
        setattr(cls, f"_{cls.__name__}__dotenv", dotenv)
        setattr(cls, f"_{cls.__name__}__dotenv_path", dotenv_path)

        cls.pre_setup()
        cls.setup(stack_level=2)
        cls.post_setup()

    @staticmethod
    def load_dotenv(*, dotenv_path: StrPath | None = None) -> dict[str, str]:  # pragma: no cover
        """Load the `.env` file and return the values."""
        if dotenv_path is None:
            dotenv_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
        return dotenv_values(dotenv_path=dotenv_path)

    @classmethod
    def pre_setup(cls) -> None:
        """
        Hook for doing additional setup before the settings have been loaded,
        but after the `.env` file has been loaded.
        """

    @classmethod
    def setup(cls, *, stack_level: int = 1) -> None:
        """Load settings and set them in the module globals where the environment is defined."""
        settings = cls.load_settings()
        stack = inspect.stack()
        module_globals: dict[str, Any] = stack[stack_level].frame.f_globals
        module_globals.update(**settings)

    @classmethod
    def post_setup(cls) -> None:
        """Hook for doing additional setup after the settings have been loaded."""

    @classmethod
    def load_settings(cls) -> dict[str, Any]:
        """Load the settings from the environment, validating and returning them."""
        return {name: getattr(cls, name) for name in dir(cls) if name.isupper() and not name.startswith("_")}

    @classproperty
    def dotenv(cls) -> dict[str, str] | Undefined:  # noqa: N805
        return getattr(cls, f"_{cls.__name__}__dotenv", Undefined)

    @classproperty
    def dotenv_path(cls) -> str | None | Undefined:  # noqa: N805
        return getattr(cls, f"_{cls.__name__}__dotenv_path", Undefined)
