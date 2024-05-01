import re

import pytest

from env_config import Environment, values
from env_config.constants import Undefined
from env_config.errors import MissingEnvValueError
from tests.helpers import set_dotenv, set_environ


@set_dotenv("Test", FOO="bar")
def test_environment__load_dotenv():
    class Test(Environment):
        pass

    assert Test.dotenv == {"FOO": "bar"}


@set_dotenv("Test", FOO="bar")
def test_environment__dont_load_dotenv_if_env_not_match():
    class Prod(Environment):
        pass

    assert Prod.dotenv == Undefined


def test_environment__subclassed():
    with set_dotenv("Common", FOO="1"):

        class Common(Environment):
            FOO = values.StringValue()

    with set_dotenv("Test", FOO="2"):

        class Test(Common):
            pass  # Field not redefined, but different env-value

    assert Common.dotenv == {"FOO": "1"}
    assert Test.dotenv == {"FOO": "2"}

    assert Common.FOO == "1"
    assert Test.FOO == "2"


@set_dotenv("Test", FOO="bar")
def test_environment__set_globals():
    class Test(Environment):
        FOO = values.StringValue()

    assert Test.FOO == "bar"
    assert globals()["FOO"] == "bar"


@set_dotenv("Test", FOO="bar")
def test_environment__set_globals__classproperty():
    class Test(Environment):
        FOO = values.StringValue()

        @classmethod
        @property
        def BAR(cls):
            return f"{cls.FOO.upper()}"

    assert Test.FOO == "bar"
    assert Test.BAR == "BAR"
    assert globals()["FOO"] == "bar"
    assert globals()["BAR"] == "BAR"


@set_dotenv("Test", FIZZ="buzz")
def test_environment__no_data():
    msg = "Value 'FOO' in environment 'Test' not defined in the .env file and value does not have a default"
    with pytest.raises(MissingEnvValueError, match=re.escape(msg)):

        class Test(Environment):
            FOO = values.StringValue()


@set_dotenv("Test", FOO="bar")
def test_environment__no_dotenv():
    msg = "Value 'FOO' in environment 'Test' needs a default value since environment does not define a `dotenv_path`"
    with pytest.raises(MissingEnvValueError, match=re.escape(msg)):

        class Test(Environment, dotenv_path=None):
            FOO = values.StringValue()


@set_environ("Test", FOO="bar")
def test_environment__use_environ():
    class Test(Environment, use_environ=True):
        FOO = values.StringValue()

    assert Test.FOO == "bar"


@set_dotenv("Test")
def test_environment__default():
    class Test(Environment):
        FOO = values.StringValue(default="fizzbuzz")

    assert Test.FOO == "fizzbuzz"


@set_dotenv("Test")
def test_environment__default__null():
    class Test(Environment):
        FOO = values.StringValue(default=None)

    assert Test.FOO is None


@set_dotenv("Test", FIZZ="buzz")
def test_environment__env_name():
    class Test(Environment):
        FOO = values.StringValue(env_name="FIZZ")

    assert Test.FOO == "buzz"


@set_dotenv("Test", FOO="bar")
def test_environment__env_name__null():
    with pytest.raises(MissingEnvValueError):

        class Test(Environment):
            FOO = values.StringValue(env_name=None)


@set_dotenv("Test", FOO="bar")
def test_environment__env_name__null__default():
    class Test(Environment):
        FOO = values.StringValue(default="foo", env_name=None)

    assert Test.FOO == "foo"
