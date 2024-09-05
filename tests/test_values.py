import re
from decimal import Decimal, InvalidOperation
from json import JSONDecodeError
from pathlib import Path
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from env_config import Environment, values
from tests.helpers import set_dotenv


@set_dotenv("Test", FOO="bar")
def test_environment__string_value():
    class Test(Environment):
        FOO = values.StringValue()

    assert Test.FOO == "bar"


@pytest.mark.parametrize("value", ["true", "True", "1", "yes"])
def test_environment__boolean_value__truthy(value):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.BooleanValue()

    assert Test.FOO is True


@pytest.mark.parametrize("value", ["false", "False", "0", "no", ""])
def test_environment__boolean_value__falsy(value):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.BooleanValue()

    assert Test.FOO is False


@pytest.mark.parametrize("value", ["1.0", "None", "foo"])
def test_environment__boolean_value__invalid(value):
    msg = f"Cannot interpret {value!r} as a boolean value"
    with set_dotenv("Test", FOO=value), pytest.raises(ValueError, match=re.escape(msg)):

        class Test(Environment):
            FOO = values.BooleanValue()


def test_environment__boolean_value__default():
    with set_dotenv("Test"):

        class Test(Environment):
            FOO = values.BooleanValue(default=True)

    assert Test.FOO is True


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("0", 0),
        ("1", 1),
        ("-1", -1),
        ("+1", 1),
        ("100_000", 100_000),
    ],
)
def test_environment__integer_value(value, result):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.IntegerValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ["foo", "1.0", "None", ""])
def test_environment__integer_value__invalid(value):
    with set_dotenv("Test", FOO=value), pytest.raises(ValueError):

        class Test(Environment):
            FOO = values.IntegerValue()


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("0", 0),
        ("1", 1),
        ("100_000", 100_000),
    ],
)
def test_environment__positive_integer_value(value, result):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.PositiveIntegerValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ["-1", "-100_000"])
def test_environment__integer_value__invalid(value):
    with set_dotenv("Test", FOO=value), pytest.raises(ValueError):

        class Test(Environment):
            FOO = values.PositiveIntegerValue()


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("0.0", 0.0),
        ("0.1", 0.1),
        ("-0.1", -0.1),
        ("0.30000000000000004", 0.30000000000000004),
        ("100_000.000_001", 100_000.000_001),
        ("1", 1.0),
        ("-1", -1.0),
    ],
)
def test_environment__float_value(value, result):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.FloatValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ["foo", "None", ""])
def test_environment__float_value__invalid(value):
    with set_dotenv("Test", FOO=value), pytest.raises(ValueError):

        class Test(Environment):
            FOO = values.FloatValue()


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("0.0", Decimal("0.0")),
        ("0.1", Decimal("0.1")),
        ("-0.1", Decimal("-0.1")),
        ("0.30000000000000004", Decimal("0.30000000000000004")),
        ("100_000.000_001", Decimal("100_000.000_001")),
        ("1", Decimal("1.0")),
        ("-1", Decimal("-1.0")),
    ],
)
def test_environment__decimal_value(value, result):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.DecimalValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ["foo", "None", ""])
def test_environment__decimal_value__invalid(value):
    with set_dotenv("Test", FOO=value), pytest.raises(InvalidOperation):

        class Test(Environment):
            FOO = values.DecimalValue()


def test_environment__import_string_value():
    with set_dotenv("Test", FOO="env_config.base.Environment"):

        class Test(Environment):
            FOO = values.ImportStringValue()

    assert Test.FOO == "env_config.base.Environment"


@pytest.mark.parametrize("value", ["foo", "None", "this.does.not.exist"])
def test_environment__import_string_value__invalid(value):
    with set_dotenv("Test", FOO=value), pytest.raises(ImportError):

        class Test(Environment):
            FOO = values.ImportStringValue()


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("foo,bar,baz", ["foo", "bar", "baz"]),
        ("foo, bar, baz ", ["foo", "bar", "baz"]),
        ("foo,bar,baz,", ["foo", "bar", "baz"]),
        ("foo", ["foo"]),
        ("", []),
    ],
)
def test_environment__list_value(value, result):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.ListValue()

    assert result == Test.FOO


def test_environment__list_value__integer_child():
    with set_dotenv("Test", FOO="1,-2,300_000"):

        class Test(Environment):
            FOO = values.ListValue(child=values.IntegerValue())

    assert Test.FOO == [1, -2, 300_000]


@set_dotenv("Test")
def test_environment__list_value__default():
    class Test(Environment):
        FOO = values.ListValue(default=["4", "5", "6"])

    assert Test.FOO == ["4", "5", "6"]


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("foo,bar,baz", ("foo", "bar", "baz")),
        ("foo,bar,baz,", ("foo", "bar", "baz")),
        ("foo", ("foo",)),
        ("", ()),
    ],
)
def test_environment__tuple_value(value, result):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.TupleValue()

    assert result == Test.FOO


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("foo,bar,baz", {"foo", "bar", "baz"}),
        ("foo,bar,baz,", {"foo", "bar", "baz"}),
        ("foo", {"foo"}),
        ("", set()),
    ],
)
def test_environment__set_value(value, result: set):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.SetValue()

    assert result.difference(Test.FOO) == set()


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("foo=1;bar=2;baz=3", {"foo": "1", "bar": "2", "baz": "3"}),
        ("foo=1; bar = 2; baz=3 ", {"foo": "1", "bar": "2", "baz": "3"}),
        ("foo=1;bar=2;baz=3;", {"foo": "1", "bar": "2", "baz": "3"}),
        ("foo=1", {"foo": "1"}),
        ("", {}),
    ],
)
def test_environment__dict_value(value, result: dict):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.DictValue()

    assert result == Test.FOO


def test_environment__dict_value__integer_child():
    with set_dotenv("Test", FOO="foo=1;bar=-2;baz=300_000"):

        class Test(Environment):
            FOO = values.DictValue(child=values.IntegerValue())

    assert Test.FOO == {"foo": 1, "bar": -2, "baz": 300_000}


def test_environment__dict_value__invalid():
    msg = "Cannot split key-value pair from 'bar2'"
    with set_dotenv("Test", FOO="foo=1;bar2"), pytest.raises(ValueError, match=re.escape(msg)):

        class Test(Environment):
            FOO = values.DictValue()


@set_dotenv("Test")
def test_environment__dict_value__default():
    class Test(Environment):
        FOO = values.DictValue(default={"foo": "bar"})

    assert Test.FOO == {"foo": "bar"}


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ('{"foo": "1"}', {"foo": "1"}),
        ('{"foo": 1}', {"foo": 1}),
        ('[{"foo": "1"}]', [{"foo": "1"}]),
        ("{}", {}),
        ("[]", []),
        ("null", None),
    ],
)
def test_environment__json_value(value, result):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.JsonValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ['{"foo":}', "", " "])
def test_environment__json_value__invalid(value):
    with set_dotenv("Test", FOO=value), pytest.raises(JSONDecodeError):

        class Test(Environment):
            FOO = values.JsonValue()


@set_dotenv("Test")
def test_environment__json_value__default():
    class Test(Environment):
        FOO = values.JsonValue(default={"foo": "bar"})

    assert Test.FOO == {"foo": "bar"}


@pytest.mark.parametrize(
    "value",
    [
        "foo@email.com",
        "foo.bar@example.net",
    ],
)
def test_environment__email_value(value):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.EmailValue()

    assert value == Test.FOO


@pytest.mark.parametrize(
    "value",
    [
        "foo@email",
        "foo.bar@",
        "None",
        "",
    ],
)
def test_environment__email_value__invalid(value):
    with set_dotenv("Test", FOO=value), pytest.raises(ValidationError):

        class Test(Environment):
            FOO = values.EmailValue()


@pytest.mark.parametrize(
    "value",
    [
        "https://www.example.com",
        "https://www.example.com/website/page",
        "https://localhost:8000/website/page",
        "https://localhost:8000/website/page?foo=bar",
    ],
)
def test_environment__url_value(value):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.URLValue()

    assert value == Test.FOO


@pytest.mark.parametrize(
    "value",
    [
        "www.example.com",
        "localhost:8000",
        "example.com",
        "example.com/website/page",
        "/website/page",
        "/website/page?foo=bar",
    ],
)
def test_environment__url_value__invalid(value):
    with set_dotenv("Test", FOO=value), pytest.raises(ValidationError):

        class Test(Environment):
            FOO = values.URLValue()


@pytest.mark.parametrize(
    "value",
    [
        "127.0.0.1",
        "192.168.8.1",
        "254.222.22.162",
        "3f7f:b7e1:b838:19d0:15b0:19dc:2343:72e1",
    ],
)
def test_environment__ip_value(value):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.IPValue()

    assert value == Test.FOO


@pytest.mark.parametrize(
    "value",
    [
        "localhost",
        "None",
        "",
    ],
)
def test_environment__ip_value__invalid(value):
    with set_dotenv("Test", FOO=value), pytest.raises(ValidationError):

        class Test(Environment):
            FOO = values.IPValue()


@pytest.mark.parametrize(
    ("regex", "value"),
    [
        (r"\d\d\d", "123"),
        (r"^[1-9]{2}$", "42"),
    ],
)
def test_environment__regex_value(regex, value):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.RegexValue(regex=regex)

    assert value == Test.FOO


@pytest.mark.parametrize(
    ("regex", "value"),
    [
        (r"\d\d\d", "foo"),
        (r"^[1-9]{2}$", "422"),
    ],
)
def test_environment__regex_value__invalid(regex, value):
    with set_dotenv("Test", FOO=value), pytest.raises(ValidationError):

        class Test(Environment):
            FOO = values.RegexValue(regex=regex)


@pytest.mark.parametrize("regex", [r"[", r"*"])
def test_environment__regex_value__invalid_regex(regex):
    with set_dotenv("Test", FOO=""), pytest.raises(re.error):

        class Test(Environment):
            FOO = values.RegexValue(regex=regex)


@pytest.mark.parametrize(
    ("value", "result"),
    [
        (str(Path(__file__)), str(Path(__file__))),
        (str(Path(__file__).parent), str(Path(__file__).parent)),
        ("./foo", str(Path.cwd() / "foo")),
        ("foo/", str(Path.cwd() / "foo")),
        ("foo", str(Path.cwd() / "foo")),
    ],
)
def test_environment__path_value(value, result):
    with set_dotenv("Test", FOO=value):

        class Test(Environment):
            FOO = values.PathValue(check_exists=False)

    assert result == Test.FOO


def test_environment__path_value__check_exists():
    value = (Path.cwd() / "foo").absolute()
    msg = f"Path '{value}' does not exist"
    with set_dotenv("Test", FOO="foo"), pytest.raises(ValueError, match=re.escape(msg)):

        class Test(Environment):
            FOO = values.PathValue()

        assert Test.FOO


def test_environment__path_value__create_if_missing():
    path = (Path.cwd() / "foo").absolute()
    with (
        set_dotenv("Test", FOO="foo"),
        patch("env_config.values.Path.mkdir") as create,
        patch("env_config.values.Path.exists", return_value=True),
    ):

        class Test(Environment):
            FOO = values.PathValue(create_if_missing=True)

    assert str(path) == Test.FOO
    assert create.called


@pytest.mark.parametrize(
    ("value", "result"),
    [
        (
            "sqlite:////absolute/path/to/db/file.db",
            {
                "default": {
                    "CONN_HEALTH_CHECKS": False,
                    "CONN_MAX_AGE": 0,
                    "DISABLE_SERVER_SIDE_CURSORS": False,
                    "ENGINE": "django.db.backends.sqlite3",
                    "HOST": "",
                    "NAME": "/absolute/path/to/db/file.db",
                    "PASSWORD": "",
                    "PORT": "",
                    "USER": "",
                }
            },
        ),
        (
            "mysql://user:password@host:8000/dbname",
            {
                "default": {
                    "CONN_HEALTH_CHECKS": False,
                    "CONN_MAX_AGE": 0,
                    "DISABLE_SERVER_SIDE_CURSORS": False,
                    "ENGINE": "django.db.backends.mysql",
                    "HOST": "host",
                    "NAME": "dbname",
                    "PASSWORD": "password",
                    "PORT": 8000,
                    "USER": "user",
                }
            },
        ),
        (
            "postgres://user:password@host:8000/dbname",
            {
                "default": {
                    "CONN_HEALTH_CHECKS": False,
                    "CONN_MAX_AGE": 0,
                    "DISABLE_SERVER_SIDE_CURSORS": False,
                    "ENGINE": "django.db.backends.postgresql",
                    "HOST": "host",
                    "NAME": "dbname",
                    "PASSWORD": "password",
                    "PORT": 8000,
                    "USER": "user",
                }
            },
        ),
        (
            "postgis://user:password@host:8000/dbname",
            {
                "default": {
                    "CONN_HEALTH_CHECKS": False,
                    "CONN_MAX_AGE": 0,
                    "DISABLE_SERVER_SIDE_CURSORS": False,
                    "ENGINE": "django.contrib.gis.db.backends.postgis",
                    "HOST": "host",
                    "NAME": "dbname",
                    "PASSWORD": "password",
                    "PORT": 8000,
                    "USER": "user",
                }
            },
        ),
    ],
)
def test_environment__database_url(value, result):
    with set_dotenv("Test", DATABASE_URL=value):

        class Test(Environment):
            DATABASES = values.DatabaseURLValue()

    assert result == Test.DATABASES


def test_environment__database_url__from_dict_default():
    databases = {
        "CONN_HEALTH_CHECKS": False,
        "CONN_MAX_AGE": 0,
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": "host",
        "NAME": "dbname",
        "PASSWORD": "password",
        "PORT": 8000,
        "USER": "user",
    }

    with set_dotenv("Test"):

        class Test(Environment):
            DATABASES = values.DatabaseURLValue(default=databases)

    assert Test.DATABASES == {"default": databases}


def test_environment__database_url__from_str_default():
    with set_dotenv("Test"):

        class Test(Environment):
            DATABASES = values.DatabaseURLValue(default="postgis://user:password@host:8000/dbname")

    assert Test.DATABASES == {
        "default": {
            "CONN_HEALTH_CHECKS": False,
            "CONN_MAX_AGE": 0,
            "DISABLE_SERVER_SIDE_CURSORS": False,
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "HOST": "host",
            "NAME": "dbname",
            "PASSWORD": "password",
            "PORT": 8000,
            "USER": "user",
        }
    }


def test_environment__database_url__params():
    with set_dotenv("Test", DATABASE_URL="postgis://user:password@host:8000/dbname"):

        class Test(Environment):
            DATABASES = values.DatabaseURLValue(conn_max_age=60)

    assert Test.DATABASES == {
        "default": {
            "CONN_HEALTH_CHECKS": False,
            "CONN_MAX_AGE": 60,
            "DISABLE_SERVER_SIDE_CURSORS": False,
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "HOST": "host",
            "NAME": "dbname",
            "PASSWORD": "password",
            "PORT": 8000,
            "USER": "user",
        }
    }


def test_environment__database_url__alias():
    with set_dotenv("Test", DATABASE_URL="postgis://user:password@host:8000/dbname"):

        class Test(Environment):
            DATABASES = values.DatabaseURLValue(db_alias="testing")

    assert Test.DATABASES == {
        "testing": {
            "CONN_HEALTH_CHECKS": False,
            "CONN_MAX_AGE": 0,
            "DISABLE_SERVER_SIDE_CURSORS": False,
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "HOST": "host",
            "NAME": "dbname",
            "PASSWORD": "password",
            "PORT": 8000,
            "USER": "user",
        }
    }


@pytest.mark.parametrize(
    ("value", "result"),
    [
        (
            "redis://master:6379",
            {
                "default": {
                    "BACKEND": "django.core.cache.backends.redis.RedisCache",
                    "LOCATION": "redis://master:6379/0",
                }
            },
        ),
    ],
)
def test_environment__cache_url(value, result):
    with set_dotenv("Test", CACHE_URL=value):

        class Test(Environment):
            CACHES = values.CacheURLValue()

    assert result == Test.CACHES


def test_environment__cache_url__from_dict_default():
    caches = {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://master:6379/0",
    }

    with set_dotenv("Test"):

        class Test(Environment):
            CACHES = values.CacheURLValue(default=caches)

    assert Test.CACHES == {"default": caches}


def test_environment__cache_url__from_str_default():
    with set_dotenv("Test"):

        class Test(Environment):
            CACHES = values.CacheURLValue(default="redis://master:6379")

    assert Test.CACHES == {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": "redis://master:6379/0",
        }
    }

