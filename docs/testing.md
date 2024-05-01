# Testing

This library provides integration with the [pytest] testing framework.
The integration provides an easy way to configure the used Environment
when running tests by setting the `DJANGO_SETTINGS_ENVIRONMENT`
configuration variable.

```ini
[pytest]
DJANGO_SETTINGS_ENVIRONMENT=Example
```

Alternatively, you can use do the same in a `pyproject.toml` file:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_ENVIRONMENT = "Example"
```


[pytest]: https://docs.pytest.org/en/latest/
