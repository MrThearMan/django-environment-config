from __future__ import annotations

import sys
from typing import Any, Callable, Generator, Generic, Mapping, ParamSpec, Sequence, TypedDict, TypeVar

if sys.version_info < (3, 12):  # pragma: no cover
    from typing_extensions import Unpack
else:
    from typing import Unpack

__all__ = [
    "Any",
    "CacheConfig",
    "Callable",
    "DBConfig",
    "DBConfigExtra",
    "Generator",
    "Generic",
    "Mapping",
    "ParamSpec",
    "Sequence",
    "TypeVar",
    "Unpack",
]


class DBConfig(TypedDict, total=False):
    ATOMIC_REQUESTS: bool
    AUTOCOMMIT: bool
    CONN_MAX_AGE: int | None
    CONN_HEALTH_CHECKS: bool
    DISABLE_SERVER_SIDE_CURSORS: bool
    ENGINE: str
    HOST: str
    NAME: str
    OPTIONS: dict[str, Any] | None
    PASSWORD: str
    PORT: str | int
    TEST: dict[str, Any]
    TIME_ZONE: str
    USER: str


class DBConfigExtra(TypedDict, total=False):
    engine: str | None
    conn_max_age: int | None
    conn_health_checks: bool
    ssl_require: bool
    test_options: dict | None


class CacheConfig(TypedDict, total=False):
    BACKEND: str
    KEY_FUNCTION: str
    KEY_PREFIX: str
    LOCATION: str
    OPTIONS: dict[str, Any]
    TIMEOUT: int
    VERSION: int
