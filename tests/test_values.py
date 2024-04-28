import re
from decimal import Decimal, InvalidOperation
from json import JSONDecodeError
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError

from env_config import Environment, values
from tests.helpers import set_dotenv


@set_dotenv(FOO="bar")
def test_environment__string_value():
    class Test(Environment):
        FOO = values.StringValue()

    assert Test.FOO == "bar"


def test_environment__string_value__default():
    class Test(Environment):
        FOO = values.StringValue(default="fizzbuzz")

    assert Test.FOO == "fizzbuzz"


@pytest.mark.parametrize("value", ["true", "True", "1", "yes"])
def test_environment__boolean_value__truthy(value):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.BooleanValue()

    assert Test.FOO is True


@pytest.mark.parametrize("value", ["false", "False", "0", "no", ""])
def test_environment__boolean_value__falsy(value):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.BooleanValue()

    assert Test.FOO is False


@pytest.mark.parametrize("value", ["1.0", "None", "foo"])
def test_environment__boolean_value__invalid(value):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.BooleanValue()

    msg = f"Cannot interpret {value!r} as a boolean value"
    with pytest.raises(ValueError, match=re.escape(msg)):
        assert Test.FOO


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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.IntegerValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ["foo", "1.0", "None", ""])
def test_environment__integer_value__invalid(value):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.IntegerValue()

    with pytest.raises(ValueError):
        assert Test.FOO


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("0", 0),
        ("1", 1),
        ("100_000", 100_000),
    ],
)
def test_environment__positive_integer_value(value, result):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.PositiveIntegerValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ["-1", "-100_000"])
def test_environment__integer_value__invalid(value):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.PositiveIntegerValue()

    with pytest.raises(ValueError):
        assert Test.FOO


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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.FloatValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ["foo", "None", ""])
def test_environment__float_value__invalid(value):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.FloatValue()

    with pytest.raises(ValueError):
        assert Test.FOO


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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.DecimalValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ["foo", "None", ""])
def test_environment__decimal_value__invalid(value):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.DecimalValue()

    with pytest.raises(InvalidOperation):
        assert Test.FOO


def test_environment__import_string_value():
    with set_dotenv(FOO="env_config.base.Environment"):

        class Test(Environment):
            FOO = values.ImportStringValue()

    assert Test.FOO == "env_config.base.Environment"


@pytest.mark.parametrize("value", ["foo", "None", "this.does.not.exist"])
def test_environment__import_string_value__invalid(value):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.ImportStringValue()

    with pytest.raises(ImportError):
        assert Test.FOO


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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.ListValue()

    assert result == Test.FOO


def test_environment__list_value__integer_child():
    with set_dotenv(FOO="1,-2,300_000"):

        class Test(Environment):
            FOO = values.ListValue(child=values.IntegerValue())

    assert Test.FOO == [1, -2, 300_000]


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
    with set_dotenv(FOO=value):

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
    with set_dotenv(FOO=value):

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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.DictValue()

    assert result == Test.FOO


def test_environment__dict_value__integer_child():
    with set_dotenv(FOO="foo=1;bar=-2;baz=300_000"):

        class Test(Environment):
            FOO = values.DictValue(child=values.IntegerValue())

    assert Test.FOO == {"foo": 1, "bar": -2, "baz": 300_000}


def test_environment__dict_value__invalid():
    with set_dotenv(FOO="foo=1;bar2"):

        class Test(Environment):
            FOO = values.DictValue()

    msg = "Cannot split key-value pair from 'bar2'"
    with pytest.raises(ValueError, match=re.escape(msg)):
        assert Test.FOO


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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.JsonValue()

    assert result == Test.FOO


@pytest.mark.parametrize("value", ['{"foo":}', "", " "])
def test_environment__json_value__invalid(value):
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.JsonValue()

    with pytest.raises(JSONDecodeError):
        assert Test.FOO


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
    with set_dotenv(FOO=value):

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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.EmailValue()

    with pytest.raises(ValidationError):
        assert Test.FOO


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
    with set_dotenv(FOO=value):

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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.URLValue()

    with pytest.raises(ValidationError):
        assert Test.FOO


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
    with set_dotenv(FOO=value):

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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.IPValue()

    with pytest.raises(ValidationError):
        assert Test.FOO


@pytest.mark.parametrize(
    ("regex", "value"),
    [
        (r"\d\d\d", "123"),
        (r"^[1-9]{2}$", "42"),
    ],
)
def test_environment__regex_value(regex, value):
    with set_dotenv(FOO=value):

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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.RegexValue(regex=regex)

    with pytest.raises(ValidationError):
        assert Test.FOO


@pytest.mark.parametrize("regex", [r"[", r"*"])
def test_environment__regex_value__invalid_regex(regex):
    with set_dotenv(FOO=""):

        class Test(Environment):
            FOO = values.RegexValue(regex=regex)

    with pytest.raises(re.error):
        assert Test.FOO


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
    with set_dotenv(FOO=value):

        class Test(Environment):
            FOO = values.PathValue(check_exists=False)

    assert result == Test.FOO


def test_environment__path_value__check_exists():
    with set_dotenv(FOO="foo"):

        class Test(Environment):
            FOO = values.PathValue()

    value = (Path.cwd() / "foo").absolute()
    msg = f"Path '{value}' does not exist"
    with pytest.raises(ValueError, match=re.escape(msg)):
        assert Test.FOO


@pytest.mark.parametrize(
    ("value", "result"),
    [
        (
            "sqlite:////absolute/path/to/db/file.db",
            {
                "default": {
                    "CONN_HEALTH_CHECKS": False,
                    "CONN_MAX_AGE": 0,
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
    with set_dotenv(DATABASE_URL=value):

        class Test(Environment):
            DATABASES = values.DatabaseURLValue()

    assert result == Test.DATABASES


def test_environment__database_url__params():
    with set_dotenv(DATABASE_URL="postgis://user:password@host:8000/dbname"):

        class Test(Environment):
            DATABASES = values.DatabaseURLValue(conn_max_age=60)

    assert Test.DATABASES == {
        "default": {
            "CONN_HEALTH_CHECKS": False,
            "CONN_MAX_AGE": 60,
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "HOST": "host",
            "NAME": "dbname",
            "PASSWORD": "password",
            "PORT": 8000,
            "USER": "user",
        }
    }


def test_environment__database_url__alias():
    with set_dotenv(DATABASE_URL="postgis://user:password@host:8000/dbname"):

        class Test(Environment):
            DATABASES = values.DatabaseURLValue(db_alias="testing")

    assert Test.DATABASES == {
        "testing": {
            "CONN_HEALTH_CHECKS": False,
            "CONN_MAX_AGE": 0,
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
    with set_dotenv(CACHE_URL=value):

        class Test(Environment):
            CACHES = values.CacheURLValue()

    assert result == Test.CACHES
