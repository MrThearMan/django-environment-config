import re

import pytest

from env_config import Environment, values
from env_config.constants import ENV_NAME, Undefined
from env_config.decorators import classproperty
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

        @classproperty
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


@set_dotenv("Test", FOO="bar")
def test_environment__overrides_from():
    class Overrides:
        FOO = "foo"

    class Test(Environment, overrides_from=Overrides):
        FOO = values.StringValue()

    assert Test.FOO == "foo"


@set_dotenv("Test")
def test_environment__overrides_from__value_descriptor():
    class Overrides:
        FOO = values.StringValue(default="foo")

    class Test(Environment, overrides_from=Overrides):
        FOO = values.StringValue()

    assert Test.FOO == "foo"


@set_dotenv("Test", FOO="foo")
def test_environment__overrides_from__value_descriptor__no_default():
    class Overrides:
        FOO = values.StringValue()

    class Test(Environment, overrides_from=Overrides):
        FOO = values.StringValue(default="bar")

    assert Test.FOO == "foo"


@set_dotenv("Test", FOO="bar")
def test_environment__overrides_from__pre_setup():
    class Overrides:
        FOO = "foo"

        @classmethod
        def pre_setup(cls):
            cls.FOO = "baz"

    class Test(Environment, overrides_from=Overrides):
        FOO = values.StringValue()

    assert Test.FOO == "baz"


@set_dotenv("Test", FOO="bar")
def test_environment__overrides_from__post_setup():
    class Overrides:
        FOO = "foo"

        @classmethod
        def post_setup(cls):
            cls.FOO = "baz"

    class Test(Environment, overrides_from=Overrides):
        FOO = values.StringValue()

    assert Test.FOO == "baz"


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


def test_environment__env_name_not_set(monkeypatch):
    monkeypatch.delenv(ENV_NAME, raising=False)

    msg = f"Environment variable {ENV_NAME!r} must be set before subclassing 'Environment'"
    with pytest.raises(ValueError, match=re.escape(msg)):

        class Test(Environment):
            pass


def test_environment__dotenv_path(monkeypatch, tmp_path):
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("FOO=bar\n", encoding="utf-8")
    monkeypatch.setenv(ENV_NAME, "Test")

    class Test(Environment, dotenv_path=dotenv_path):
        FOO = values.StringValue()

    assert Test.dotenv_path == dotenv_path
    assert Test.FOO == "bar"


def test_environment__find_dotenv(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("FOO=bar\n", encoding="utf-8")
    monkeypatch.setenv(ENV_NAME, "Test")

    # The `.env` file is searched from the directory of the module that defines the environment,
    # so the environment is defined in a module that is "located" in the temporary directory.
    code = "from env_config import Environment, values\n\nclass Test(Environment):\n    FOO = values.StringValue()\n"
    module_globals = {}
    exec(compile(code, str(tmp_path / "settings.py"), "exec"), module_globals)

    assert module_globals["FOO"] == "bar"


def test_undefined():
    assert repr(Undefined) == "Undefined"
    assert bool(Undefined) is False


def test_value__convert_not_implemented():
    with pytest.raises(NotImplementedError):
        values.Value.convert(values.StringValue(), "foo")
