# Configuration

## Loading the Environment

The library supports configurable settings using ["value descriptors"](#value-descriptors).
These descriptors are used to define settings that can change their values
based on a `.env` file or environment variables.

By default, Environment-classes will look for a `.env` file from the current
working directory up to the root using the [python-dotenv] library.

```python
from env_config import Environment, values

class Example(Environment):
    DEBUG = values.BooleanValue()
```

In case you want to use environment variables instead:

```python
from env_config import Environment, values

class Example(Environment, use_environ=True):
    DEBUG = values.BooleanValue()
```

If a value matching the setting's name is found from the configured location,
it will be used to set the value of the setting, given the specific descriptor
is able to convert it to the type it expects.

You can also set the path for the `.env` file directly if you wish.

```python
from env_config import Environment, values

class Example(Environment, dotenv_path="/path/to/.env"):
    DEBUG = values.BooleanValue()
```

Or you can disable the loading the `.env` file altogether.

```python
from env_config import Environment, values

class Example(Environment, dotenv_path=None):
    DEBUG = values.BooleanValue()
```

However, doing this with the above configuration will raise an error,
since we cannot determine the value for `DEBUG`. Similarly, an error would be raised
if the `.env` if loaded, but it does not contain a matching value for the setting.

Therefore, we must set a default value in the descriptor for these cases.

```python
from env_config import Environment, values

class Example(Environment):
    DEBUG = values.BooleanValue(default=False)
```

The default value can also be `None`, but note that doing this will also skip
the normal value conversion based on the descriptor type.

In case the name of the setting in the `.env` file or environment is different from the
name of the setting in the Environment class, you can specify the name of the matching
setting in the descriptor using `env_name`.

```python
from env_config import Environment, values

class Example(Environment):
    DEBUG = values.BooleanValue(env_name="DJANGO_DEBUG_MODE")
```

Setting `env_name` to `None` will make the descriptor always use the default value,
even if the loaded environment contains a value for the setting. This can be useful
if the value descriptor contains some useful validation or conversion logic that you
want to use when setting the value.

## Value Descriptors

### Value

The base class for all value descriptors. This is an abstract class that can't be
used directly. All subclasses must implement the `convert` method, and can be initialized
with the following arguments:

- `default`: The default value for the setting. If not set, a value for the setting
  must be found from the `.env` file or environment, or an exception will be raised.
- `env_name`: The name of the setting in the `.env` file or environment. If not set,
  the name of the setting in the Environment class is used. If set to `None`, the
  descriptor will always use the `default` value.

### StringValue

A value descriptor for string values. The `convert` method will return the value as is.

### BooleanValue

A value descriptor for boolean values. The `convert` method will return `True` if the
value is one of the following (case-insensitive): `yes`, `y`, `true`, `1` or `False`
if it's one of the following (case-insensitive): `no`, `n`, `false`, `0` or `""`.
Otherwise, an exception will be raised.

### IntegerValue

A value descriptor for integer values. The `convert` method will return the value as an
integer if it can be converted. Otherwise, an exception will be raised.

### PositiveIntegerValue

A value descriptor for positive integer values. The `convert` method will return the value
as an integer if it can be converted and is greater than zero. Otherwise, an exception will
be raised.

### FloatValue

A value descriptor for float values. The `convert` method will return the value as a float
if it can be converted. Otherwise, an exception will be raised.

### DecimalValue

A value descriptor for decimal values. The `convert` method will return the value as a
decimal if it can be converted. Otherwise, an exception will be raised.

### ImportStringValue

A value descriptor for string values that should be importable. The `convert` method will
return the imported value if it can be imported. Otherwise, an exception will be raised.


### SequenceValue

An abstract value descriptor for sequences like lists, tuples, and sets. Cannot be used directly.
Accepts the following additional arguments:

- `child`: A value descriptor to use for the list items. If not set, the items will
  be returned as strings.
- `delimiter`: The delimiter to use when splitting the string into a list. Defaults to `,`.

### ListValue

A [SequenceValue](#SequenceValue) descriptor for lists. The `convert` method will return the value as a
list if it can be converted. Otherwise, an exception will be raised.

### TupleValue

A [SequenceValue](#SequenceValue) descriptor for tuples. The `convert` method will return the value as a
tuple if it can be converted. Otherwise, an exception will be raised.

### SetValue

A [SequenceValue](#SequenceValue) descriptor for sets. The `convert` method will return the value as a
sets if it can be converted. Otherwise, an exception will be raised.

### MappingValue

An abstract value descriptor for sequences like dicts. Cannot be used directly.
Accepts the following additional arguments:

- `child`: A value descriptor to use for the dict values. If not set, the items will
  be returned as strings.
- `kv_delimiter`: The delimiter to use when splitting items into keys and values. Defaults to `=`.
- `item_delimiter`: The delimiter to use when splitting the string list of key-value pairs. Defaults to `;`.

### DictValue

A [MappingValue](#MappingValue) descriptor for dicts. The `convert` method will return the value as a
dict if it can be converted. Otherwise, an exception will be raised.

### JsonValue

A value descriptor for JSON values. The `convert` method will return the value as a
valid JSON value if it can be converted. Otherwise, an exception will be raised.

### EmailValue

A value descriptor for email values. The `convert` method will return the value as is
if it's a valid email address. Otherwise, an exception will be raised.

### URLValue

A value descriptor for URL values. The `convert` method will return the value as is
if it's a valid URL. Otherwise, an exception will be raised.

### IPValue

A value descriptor for IP address values. The `convert` method will return the value as is
if it's a valid IP address. Otherwise, an exception will be raised.

### RegexValue

A value descriptor for values that should match a regular expression.
Accepts the following additional arguments:

- `regex`: The regular expression pattern to match.

The `convert` method will return the value as is if it matches the regular expression.
Otherwise, an exception will be raised.

### PathValue

A value descriptor for directory path values. Accepts the following additional arguments:

- `check_exists`: Whether to check if the path exists or not. Defaults to `True`.
- `create_if_missing`: If `True`, create the path if it doesn't exist. Defaults to `False`.
- `mode`: The mode to use when creating the path if it doesn't exist. Defaults to `0o777`.

The `convert` method will return the value as is if it's a valid directory path.
Otherwise, an exception will be raised.

### DatabaseURLValue

> Requires the `db` extra dependency to be installed.
> ```
> pip install django-environment-config[db]
> ```

A value descriptor for configuring the `DATABASES` setting in Django. It uses the [dj_database_url]
library to parse the setting from a `DATABASE_URL` environment variable. See the library for more details.

The `convert` method will convert the value to a dictionary that can be used as the `DATABASES` setting,
if it can be parsed. Otherwise, an exception will be raised.

### CacheURLValue

> Requires the `cache` extra dependency to be installed.
> ```
> pip install django-environment-config[cache]
> ```

A value descriptor for configuring the `CACHES` setting in Django. It uses the [django_cache_url]
library to parse the setting from a `CACHE_URL` environment variable. See the library for more details.

The `convert` method will convert the value to a dictionary that can be used as the `CACHES` setting,
if it can be parsed. Otherwise, an exception will be raised.

## Computed properties

In addition to value descriptors and regular class attributes, you can also use
classproperties to define computed settings. This can be useful if the setting
requires values from other settings.

```python
from env_config import Environment, values
from env_config.decorators import classproperty

class Example(Environment):
    DEBUG = values.BooleanValue(default=False)

    @classproperty
    def LOG_LEVEL(cls):
        return "DEBUG" if cls.DEBUG else "INFO"
```

> Note that value descriptors are only bound to the environment values _after_
> the class is created, so if you try to use them in the class body before that,
> they will be plain classes, not descriptors.
>
> ```python
> from env_config import Environment, values
>
> class Example(Environment):
>     DEBUG = values.BooleanValue(default=False)
>
>     # Debug is still a BoolenValue instance, not a descriptor.
>     # It will always be truthy, and so LOG_LEVEL will always be "DEBUG".
>     LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
>```

## Configuration mixins

Mixin-classes can be a useful way to reuse setting for multiple environments.
Remember to add the mixin first, and the Environment second.

```python
from env_config import Environment

class Defaults:
    ADMINS = []
    ...

class Local(Defaults, Environment):
    pass

class Prod(Defaults, Environment):
    pass
```

Note, however, that mixins will not override values defined on the inheriting class.
For this, use the [overrides](#overrides) feature.

## Overrides

For local development, one useful pattern for overriding settings is to provide
a `local_settings.py` file that is ignored from versioning, and contains a mixin
for overriding settings locally. This mixin can then be imported to the `settings.py`
file, and added to the Environment using the `overrides_from` argument. This way,
any settings defined in the mixin will be used, even if the same settings are
also defined in the created Environment itself.

```python
# local_settings.py

class LocalOverrides:
    DEBUG = True
```

```python
# settings.py

from env_config import Environment

# Import mixin which is ignored from version control.
# Catch import errors, since the mixin is not there in production.
try:
    from local_settings import LocalOverrides
except ImportError:
    class LocalOverrides: ...

class Example(Environment, overrides_from=LocalOverrides):
    pass
```


[python-dotenv]: https://github.com/theskumar/python-dotenv
[dj_database_url]: https://github.com/jazzband/dj-database-url/
[django_cache_url]: https://pypi.org/project/django-cache-url/
