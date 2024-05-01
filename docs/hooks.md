# Hooks

The Environment-class provides a few hooks that can be used to add
logic to the initialization of the environment, or modify its behavior.

## `pre-setup`

This hook is called before the settings have been determined, but after the
environment has been loaded.

```python
from env_config import Environment

class Example(Environment):

    @classmethod
    def pre_setup(cls):
        ...
```

## `post-setup`

This hook is called after the settings have been determined.

```python
from env_config import Environment

class Example(Environment):

    @classmethod
    def post_setup(cls) -> None:
        ...
```

## `load_dotenv`

This method is used to load the .env file. By default, the library uses the [python-dotenv]
library to load the file. You can override this method to provide your own implementation.
It should return a mapping of the environment variables, where the keys and values are strings.

```python
from env_config import Environment
from dotenv.main import StrPath

class Example(Environment):

    @staticmethod
    def load_dotenv(*, dotenv_path: StrPath | None = None) -> dict[str, str]:
        ...
```

[python-dotenv]: https://github.com/theskumar/python-dotenv
