# Django Environment Config

[![Coverage Status][coverage-badge]][coverage]
[![GitHub Workflow Status][status-badge]][status]
[![PyPI][pypi-badge]][pypi]
[![GitHub][licence-badge]][licence]
[![GitHub Last Commit][repo-badge]][repo]
[![GitHub Issues][issues-badge]][issues]
[![Downloads][downloads-badge]][pypi]
[![Python Version][version-badge]][pypi]

```shell
pip install django-environment-config
```

---

**Documentation**: [https://mrthearman.github.io/django-environment-config/](https://mrthearman.github.io/django-environment-config/)

**Source Code**: [https://github.com/MrThearMan/django-environment-config/](https://github.com/MrThearMan/django-environment-config/)

**Contributing**: [https://github.com/MrThearMan/django-environment-config/blob/main/CONTRIBUTING.md](https://github.com/MrThearMan/django-environment-config/blob/main/CONTRIBUTING.md)

---

Inspired by [django-configurations], this library aims to provide a simple way to configure
settings for different environments in Django applications. For example, you might want to
have different settings for local development compared to production, and different still when
running automated tests or in checks in you CI.

## Overview

Environments are defined with a simple class-based configuration in the `settings.py` module.

```python
from env_config import Environment, values

class Example(Environment):
    DEBUG = True
    SECRET_KEY = values.StringValue()
    ALLOWED_HOSTS = values.ListValue(default=["*"])
    DATABASES = values.DatabaseURLValue()
```

The Environment must be selected by setting the `DJANGO_SETTINGS_ENVIRONMENT`
environment variable to the name of the class.

```shell
DJANGO_SETTINGS_ENVIRONMENT=Example python manage.py runserver
```

Check out the [docs] for more information.

[django-configurations]: https://github.com/jazzband/django-configurations
[docs]: https://mrthearman.github.io/django-environment-config/

[coverage-badge]: https://coveralls.io/repos/github/MrThearMan/django-environment-config/badge.svg?branch=main
[status-badge]: https://img.shields.io/github/actions/workflow/status/MrThearMan/django-environment-config/test.yml?branch=main
[pypi-badge]: https://img.shields.io/pypi/v/django-environment-config
[licence-badge]: https://img.shields.io/github/license/MrThearMan/django-environment-config
[repo-badge]: https://img.shields.io/github/last-commit/MrThearMan/django-environment-config
[issues-badge]: https://img.shields.io/github/issues-raw/MrThearMan/django-environment-config
[version-badge]: https://img.shields.io/pypi/pyversions/django-environment-config
[downloads-badge]: https://img.shields.io/pypi/dm/django-environment-config

[coverage]: https://coveralls.io/github/MrThearMan/django-environment-config?branch=main
[status]: https://github.com/MrThearMan/django-environment-config/actions/workflows/test.yml
[pypi]: https://pypi.org/project/django-environment-config
[licence]: https://github.com/MrThearMan/django-environment-config/blob/main/LICENSE
[repo]: https://github.com/MrThearMan/django-environment-config/commits/main
[issues]: https://github.com/MrThearMan/django-environment-config/issues
