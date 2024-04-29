from __future__ import annotations

import os

import pytest

ENV_NAME = "DJANGO_SETTINGS_ENVIRONMENT"


@pytest.hookimpl()
def pytest_addoption(parser: pytest.Parser) -> None:
    # Adds the env variable as a recognized configuration option.
    parser.addini(ENV_NAME, "`django-environment-config` class to use by pytest-django.")


# Must use `tryfirst` to set the environment variable before Django is loaded by other plugins.
@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config: pytest.Config, parser: pytest.Parser, args: list[str]) -> None:
    # Sets the environment variable to the value of the `DJANGO_SETTINGS_ENVIRONMENT` option (if it exists).
    value: str = early_config.getini(ENV_NAME)
    if value:
        os.environ.setdefault(ENV_NAME, value)
