import re

import pytest

from env_config import Environment, values
from env_config.constants import Undefined
from env_config.errors import MissingEnvValueError
from tests.helpers import set_dotenv


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
            pass

    with set_dotenv("Test", FOO="2"):

        class Test(Common):
            pass

    assert Common.dotenv == {"FOO": "1"}
    assert Test.dotenv == {"FOO": "2"}


@set_dotenv("Test", FOO="bar")
def test_environment__value_field():
    class Test(Environment):
        FOO = values.StringValue()

    assert Test.FOO == "bar"

    # Since `DJANGO_SETTINGS_ENVIRONMENT` is set to "Test", the environment
    # values are loaded from the `.env` file to the globals where the class is defined.
    assert globals()["FOO"] == "bar"


@set_dotenv("Test", FOO="bar")
def test_environment__value_property():
    class Test(Environment):
        FOO = values.StringValue()

        @classmethod
        @property
        def BAR(cls):
            return f"{cls.FOO.upper()}"

    assert Test.FOO == "bar"
    assert Test.BAR == "BAR"

    # Since `DJANGO_SETTINGS_ENVIRONMENT` is set to "Test", the environment
    # values are loaded from the `.env` file to the globals where the class is defined.
    assert globals()["FOO"] == "bar"
    assert globals()["BAR"] == "BAR"


def test_environment__value_field__subclassed():
    with set_dotenv("Common", FOO="1"):

        class Common(Environment):
            FOO = values.StringValue()

    with set_dotenv("Test", FOO="2"):

        class Test(Common):
            pass  # Field not redefined, but different env-value

    assert Common.FOO == "1"
    assert Test.FOO == "2"


@set_dotenv("Test", FIZZ="buzz")
def test_environment__value_field__no_data():
    msg = "Value 'FOO' in environment 'Test' not defined in the .env file and value does not have a default"
    with pytest.raises(MissingEnvValueError, match=re.escape(msg)):

        class Test(Environment):
            FOO = values.StringValue()


@set_dotenv("Test", FOO="bar")
def test_environment__value_field__no_dotenv():
    msg = "Value 'FOO' in environment 'Test' needs a default value since environment does not define a `dotenv_path`"
    with pytest.raises(MissingEnvValueError, match=re.escape(msg)):

        class Test(Environment, dotenv_path=None):
            FOO = values.StringValue()
