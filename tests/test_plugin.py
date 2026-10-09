import os
from unittest.mock import Mock

from env_config.constants import ENV_NAME
from env_config_pytest_plugin.hooks import pytest_load_initial_conftests


def test_plugin__set_environment(monkeypatch):
    monkeypatch.delenv(ENV_NAME, raising=False)
    config = Mock(getini=Mock(return_value="Test"))

    pytest_load_initial_conftests(early_config=config, parser=Mock(), args=[])

    config.getini.assert_called_once_with(ENV_NAME)
    assert os.environ[ENV_NAME] == "Test"


def test_plugin__no_environment_configured(monkeypatch):
    monkeypatch.delenv(ENV_NAME, raising=False)
    config = Mock(getini=Mock(return_value=""))

    pytest_load_initial_conftests(early_config=config, parser=Mock(), args=[])

    assert ENV_NAME not in os.environ
