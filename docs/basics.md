# Basics

Environments are defined with a simple class-based configuration in the `settings.py` module.

```python
from env_config import Environment

class Example(Environment):
    DEBUG = True
```

The Environment must be selected by setting the `DJANGO_SETTINGS_ENVIRONMENT` environment variable
to the name of the class. If the environment variable is not set, an exception will be raised,
since the library will not be able to determine which environment should be used.

```shell
DJANGO_SETTINGS_ENVIRONMENT=Example python manage.py runserver
```

Similarly to the [django-configurations] library, the selected Environment's upper-case class
attributes will be added as the module level global variables in the module where the environment
is defined. This happens immidiately after the Environment class is defined as part of the
class creation process.

```python
from env_config import Environment

class Example(Environment):
    DEBUG = True

    # These will not be used
    not_global = None
    _NOT_GLOBAL = None

# Exists immidiately after Example is defined,
# given `DJANGO_SETTINGS_ENVIRONMENT=Example`
print(DEBUG)
```

However, this library's implementation is much simpler and doesn't require any
additional configuration or setup. Here is the magic behind the scenes from
`env_config.base.Environment.setup`:

```python
# Inspect the call stack to find the module where the environment is defined
stack = inspect.stack()
module_globals = stack[stack_level].frame.f_globals
# Update the module's global variables with the environment's loaded settings
module_globals.update(**settings)
```

Of course, one should be a little careful that this does not override any
existing global variables in the module.

[django-configurations]: https://github.com/jazzband/django-configurations
