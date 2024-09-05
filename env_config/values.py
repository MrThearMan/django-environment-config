from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

from django.utils.module_loading import import_string

from .constants import Undefined
from .errors import MissingEnvValueError, MissingExtraDependencyError
from .typing import Any, CacheConfig, DBConfig, DBConfigExtra, Generator, Generic, Mapping, Sequence, TypeVar, Unpack

if TYPE_CHECKING:
    from .base import Environment


__all__ = [
    "BooleanValue",
    "CacheURLValue",
    "DatabaseURLValue",
    "DecimalValue",
    "DictValue",
    "EmailValue",
    "FloatValue",
    "IPValue",
    "ImportStringValue",
    "IntegerValue",
    "JsonValue",
    "ListValue",
    "MappingValue",
    "PathValue",
    "PositiveIntegerValue",
    "RegexValue",
    "SequenceValue",
    "SetValue",
    "StringValue",
    "TupleValue",
    "URLValue",
    "Value",
]


T = TypeVar("T")


class Value(ABC, Generic[T]):
    def __init__(
        self,
        *,
        default: T | None = Undefined,
        env_name: str | None | Undefined = Undefined,
    ) -> None:
        """
        Value descriptor for an environment variable.

        :param default: The default value to use if the environment variable is not set.
        :param env_name: The name of the environment variable to use. If not given, the name of the field is used.
                         Set this to `None` to skip loading the value from the environment.
        """
        self.default: T | None = default
        self.name: str = env_name
        self.skip_env: bool = env_name is None

        # Use a map to store the value per environment so that we can have
        # different values for environments what inherit from each other.
        self.value_by_environment: dict[type[Environment], Any] = defaultdict(lambda: Undefined)
        super().__init__()

    def __set_name__(self, env: type[Environment], name: str) -> None:
        """Called after the owner Environment-class is created with this field as a class attribute."""
        if self.name in (Undefined, None):
            self.name = name

    def __get__(self, _: Environment | None, env: type[Environment]) -> T:
        """Called when accessing the field on the class or an instance of the class."""
        if self.value_by_environment[env] is not Undefined:
            return self.value_by_environment[env]

        self.value_by_environment[env] = self.get_for_environment(env)
        return self.value_by_environment[env]

    def get_for_environment(self, env: type[Environment]) -> T:
        value = self.default if env.dotenv is Undefined or self.skip_env else env.dotenv.get(self.name, self.default)
        if value is Undefined:
            raise MissingEnvValueError(name=self.name, env=env)

        if value is None:
            return None

        return self.convert(value)

    @abstractmethod
    def convert(self, value: str | T) -> T:  # pragma: no cover
        """Convert the given value into the proper representation."""
        raise NotImplementedError


class StringValue(Value[str]):
    """Parses env variables into a string value."""

    def convert(self, value: str) -> str:
        return value


class BooleanValue(Value[bool]):
    """Parses env variables into a boolean value."""

    def convert(self, value: str | bool) -> bool:  # noqa: FBT001
        if isinstance(value, bool):
            return value
        normalized_value = value.strip().lower()
        if normalized_value in ("yes", "y", "true", "1"):
            return True
        if normalized_value in ("no", "n", "false", "0", ""):
            return False
        msg = f"Cannot interpret {value!r} as a boolean value"
        raise ValueError(msg)


class IntegerValue(Value[int]):
    """Parses env variables into an integer value."""

    def convert(self, value: str | int) -> int:
        return int(value)


class PositiveIntegerValue(IntegerValue):
    """Parses env variables into an integer value, and validates that the value is positive."""

    def convert(self, value: str | int) -> int:
        val = super().convert(value)
        if val < 0:
            msg = f"Value must be positive, got {val}"
            raise ValueError(msg)
        return val


class FloatValue(Value[float]):
    """Parses env variables into a float value."""

    def convert(self, value: str | float) -> float:
        return float(value)


class DecimalValue(Value[Decimal], Decimal):
    """Parses env variables into a Decimal value."""

    def convert(self, value: str | Decimal) -> Decimal:
        return Decimal(value)


class ImportStringValue(Value[str]):
    """Parses env variables into a string value, and validates that the value is an importable string."""

    def convert(self, value: str) -> str:
        import_string(value)
        return value


class SequenceValue(Value, ABC, Generic[T]):
    def __init__(
        self,
        child: Value[T] | None = None,
        *,
        default: Sequence[T] | None = Undefined,
        env_name: str | None | Undefined = Undefined,
        delimiter: str = ",",
    ) -> None:
        self.child = child or StringValue()
        self.delimiter = delimiter
        super().__init__(default=default, env_name=env_name)

    def iterate(self, value: str | Sequence[Any]) -> Generator[T, None, None]:
        seq = value.split(self.delimiter) if isinstance(value, str) else value
        for item in seq:
            if not item:
                continue

            yield self.child.convert(item.strip())


class ListValue(SequenceValue):
    """Parses env variables like `item1,item2,item3` into a list."""

    def convert(self, value: str | list[Any]) -> list[Any]:
        return list(self.iterate(value))


class TupleValue(SequenceValue):
    """Parses env variables like `item1,item2,item3` into a tuple."""

    def convert(self, value: str | tuple[Any, ...]) -> tuple[Any, ...]:
        return tuple(self.iterate(value))


class SetValue(SequenceValue):
    """Parses env variables like `item1,item2,item3` into a set."""

    def convert(self, value: str | set[str]) -> set[Any]:
        return set(self.iterate(value))


class MappingValue(Value, ABC, Generic[T]):
    def __init__(
        self,
        child: Value[T] | None = None,
        *,
        default: Mapping[str, T] | None = Undefined,
        env_name: str | None | Undefined = Undefined,
        kv_delimiter: str = "=",
        item_delimiter: str = ";",
    ) -> None:
        self.child = child or StringValue()
        self.kv_delimiter = kv_delimiter
        self.item_delimiter = item_delimiter
        super().__init__(default=default, env_name=env_name)

    def iterate(self, value: str | Mapping[str, Any]) -> Generator[tuple[str, Any], None, None]:
        seq = value.split(self.item_delimiter) if isinstance(value, str) else value.items()

        for item in seq:
            if not item:
                continue

            if isinstance(item, str):
                kv = item.split(self.kv_delimiter, 1)
                if len(kv) != 2:  # noqa: PLR2004
                    msg = f"Cannot split key-value pair from {item!r}"
                    raise ValueError(msg)
            else:
                kv = item

            yield kv[0].strip(), self.child.convert(kv[1].strip())


class DictValue(MappingValue):
    """Parses env variables like `key1=value1;key2=value2` into a dict."""

    def convert(self, value: str | dict[str, Any]) -> dict[str, Any]:
        return dict(self.iterate(value))


class JsonValue(Value[dict | list]):
    """Parses env variables from a json string to a python list or dict."""

    def convert(self, value: str | list | dict) -> list | dict:
        if isinstance(value, (list, dict)):
            return value
        return json.loads(value)


class EmailValue(StringValue):
    """Parses env variables into a string value, and validates that it's a valid email address."""

    def convert(self, value: str) -> str:
        from django.core.validators import validate_email

        validate_email(value)
        return value


class URLValue(StringValue):
    """Parses env variables into a string value, and validates that it's a valid URL."""

    def convert(self, value: str) -> str:
        from django.core.validators import URLValidator

        URLValidator()(value)
        return value


class IPValue(StringValue):
    """Parses env variables into a string value, and validates that it's a valid IP address."""

    def convert(self, value: str) -> str:
        from django.core.validators import validate_ipv46_address

        validate_ipv46_address(value)
        return value


class RegexValue(StringValue):
    """Parses env variables into a string value, and validates that it matches the given regex."""

    def __init__(
        self,
        *,
        regex: str,
        default: str | None = Undefined,
        env_name: str | None | Undefined = Undefined,
    ) -> None:
        self.regex = regex
        super().__init__(default=default, env_name=env_name)

    def convert(self, value: str) -> str:
        from django.core.validators import RegexValidator

        RegexValidator(regex=self.regex)(value)
        return value


class PathValue(StringValue):
    """Parses env variable into a string value, and can optionally validate that the path exists."""

    def __init__(
        self,
        *,
        default: str | None = Undefined,
        env_name: str | None | Undefined = Undefined,
        check_exists: bool = True,
        create_if_missing: bool = False,
        mode: int = 0o777,
    ) -> None:
        self.check_exists = check_exists
        self.create_if_missing = create_if_missing
        self.mode = mode
        super().__init__(default=default, env_name=env_name)

    def convert(self, value: str) -> str:
        path = Path(value).absolute()
        if self.create_if_missing:
            path.mkdir(mode=self.mode, parents=True, exist_ok=True)
        if self.check_exists and not path.exists():
            msg = f"Path '{path}' does not exist"
            raise ValueError(msg)

        return str(path)


class DatabaseURLValue(Value[DBConfig | str]):
    """Load a database configuration from a URL."""

    def __init__(
        self,
        *,
        db_alias: str = "default",
        default: DBConfig | str = Undefined,
        env_name: str = "DATABASE_URL",
        **params: Unpack[DBConfigExtra],
    ) -> None:
        self.db_alias = db_alias
        self.params = params
        super().__init__(default=default, env_name=env_name)

    def convert(self, value: str | DBConfig) -> dict[str, DBConfig]:
        if not isinstance(value, str):
            return {self.db_alias: value}

        try:
            from dj_database_url import parse
        except ImportError as error:  # pragma: no cover
            msg = (
                "You must install the 'db' extra dependency "
                "(e.g., `pip install django-environment-config[db]`) "
                "to use the DatabaseURLValue."
            )
            raise MissingExtraDependencyError(msg) from error

        config = parse(value, **self.params)
        return {self.db_alias: config}


class CacheURLValue(Value[CacheConfig | str]):
    """Load a cache configuration from a URL."""

    def __init__(
        self,
        *,
        cache_alias: str = "default",
        default: CacheConfig | str = Undefined,
        env_name: str = "CACHE_URL",
    ) -> None:
        self.cache_alias = cache_alias
        super().__init__(default=default, env_name=env_name)

    def convert(self, value: str | CacheConfig) -> dict[str, CacheConfig]:
        if not isinstance(value, str):
            return {self.cache_alias: value}

        try:
            from django_cache_url import parse
        except ImportError as error:  # pragma: no cover
            msg = (
                "You must install the 'cache' extra dependency "
                "(e.g., `pip install django-environment-config[cache]`) "
                "to use the CacheURLValue."
            )
            raise MissingExtraDependencyError(msg) from error

        config = parse(value)
        return {self.cache_alias: config}
