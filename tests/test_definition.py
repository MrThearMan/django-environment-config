import re

import pytest

from env_config import Environment, values
from env_config.errors import MissingEnvValueError
from tests.helpers import set_dotenv


@set_dotenv(FOO="bar")
def test_environment__load_dotenv():
    class Test(Environment):
        pass

    assert Test.dotenv == {"FOO": "bar"}


def test_environment__subclassed():
    with set_dotenv(FOO="1"):

        class Common(Environment):
            pass

    with set_dotenv(FOO="2"):

        class Test(Common):
            pass

    assert Common.dotenv == {"FOO": "1"}
    assert Test.dotenv == {"FOO": "2"}


@set_dotenv(FOO="bar")
def test_environment__value_field():
    class Load(Environment):
        FOO = values.StringValue()

    assert Load.FOO == "bar"

    # Since `DJANGO_SETTINGS_ENVIRONMENT` is set to "Test", the environment
    # values are loaded from the `.env` file to the globals where the class is defined.
    assert globals()["FOO"] == "bar"


@set_dotenv(FOO="bar")
def test_environment__value_property():
    class Load(Environment):
        FOO = values.StringValue()

        @classmethod
        @property
        def BAR(cls):
            return f"{cls.FOO.upper()}"

    assert Load.FOO == "bar"
    assert Load.BAR == "BAR"

    # Since `DJANGO_SETTINGS_ENVIRONMENT` is set to "Test", the environment
    # values are loaded from the `.env` file to the globals where the class is defined.
    assert globals()["FOO"] == "bar"
    assert globals()["BAR"] == "BAR"


def test_environment__value_field__subclassed():
    with set_dotenv(FOO="1"):

        class Common(Environment):
            FOO = values.StringValue()

    with set_dotenv(FOO="2"):

        class Test(Common):
            pass  # Field not redefined, but different env-value

    assert Common.FOO == "1"
    assert Test.FOO == "2"


@set_dotenv(FIZZ="buzz")
def test_environment__value_field__no_data():
    msg = "Value 'FOO' in environment 'Load' not defined in the .env file and value does not have a default"
    with pytest.raises(MissingEnvValueError, match=re.escape(msg)):

        class Load(Environment):
            FOO = values.StringValue()


@set_dotenv(FOO="bar")
def test_environment__value_field__no_dotenv():
    msg = "Value 'FOO' in environment 'Load' needs a default value since environment does not define a `dotenv_path`"
    with pytest.raises(MissingEnvValueError, match=re.escape(msg)):

        class Load(Environment, dotenv_path=None):
            FOO = values.StringValue()
