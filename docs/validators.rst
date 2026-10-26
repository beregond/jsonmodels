==========
Validators
==========

Validators check a value every time it is assigned to a field, and again when
the model is validated. Pass one validator, or a list of them, with the
`validators` argument. For writing your own, see :ref:`custom-validators`.

All validators below also change the generated JSON schema, see
:ref:`json-schema`.

.. warning::

   Only validators that have a `modify_schema` method show up in the generated
   JSON schema. The built-in validators have it, **custom validators don't
   unless you add it**. This includes plain functions, which can't have it.
   Such validators are still enforced in Python, but anybody validating data
   against your schema (e.g. an API client) won't see their rules.

.. note::

   Validators run for `None` too, unless the field is `nullable=True`. For
   optional fields with validators, always set `nullable=True`.

Min and Max
-----------

:class:`~jsonmodels.validators.Min` and :class:`~jsonmodels.validators.Max`
check a number against a bound. With `exclusive=True` the bound itself is
not allowed.

.. code-block:: python

    from jsonmodels import fields, models, validators

    class Product(models.Base):
        stock = fields.IntField(validators=validators.Min(0))
        rating = fields.FloatField(
            validators=[validators.Min(0), validators.Max(5, exclusive=True)]
        )

    >>> Product(stock=-1)
    *** ValidationError: Error for field 'stock': '-1' is lower than minimum ('0')..

Schema: `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`.

Length
------

:class:`~jsonmodels.validators.Length` checks `len(value)`, so it works for
strings and lists. At least one of `minimum_value` and `maximum_value` is
required.

.. code-block:: python

    class User(models.Base):
        login = fields.StringField(validators=validators.Length(3, 20))
        tags = fields.ListField(str, validators=validators.Length(maximum_value=5))

Schema: `minLength` and `maxLength` for strings, `minItems` and `maxItems`
for lists.

.. note::

   A `ListField` is an empty list by default. With a minimum length above `0`
   it will fail validation until you fill it.

To validate every single item of a list, use `item_validators`:

.. code-block:: python

    tags = fields.ListField(str, item_validators=[validators.Length(2)])

Regex
-----

:class:`~jsonmodels.validators.Regex` checks that a pattern matches
(`re.search`). Supported flags are `ignorecase` and `multiline`:

.. code-block:: python

    class User(models.Base):
        email = fields.StringField(validators=validators.Regex(r"^[^@]+@[^@]+$"))
        code = fields.StringField(validators=validators.Regex("^ab", ignorecase=True))

The pattern may also be given in the ECMA notation (`"/^ab/i"`). Then the
flags are taken from the pattern and the keyword flags are ignored. In the
schema the pattern is always written in the ECMA form.

Enum
----

:class:`~jsonmodels.validators.Enum` accepts only the listed values:

.. code-block:: python

    class Ticket(models.Base):
        status = fields.StringField(validators=validators.Enum("open", "closed"))

Schema: `enum`.

Writing your own
----------------

A validator is a function, or an object with a `validate` method. It must
raise :class:`~jsonmodels.errors.ValidationError` when the value is wrong.
See :ref:`custom-validators` for details and for `modify_schema`.

.. code-block:: python

    from jsonmodels.errors import ValidationError

    def even(value):
        if value % 2:
            raise ValidationError(f"{value} is not even")

    class Pair(models.Base):
        number = fields.IntField(validators=even)

To make a custom validator visible in the schema, make it a class with a
`modify_schema` method, which receives the schema of the single field and
changes it in place:

.. code-block:: python

    class Even:
        def validate(self, value):
            if value % 2:
                raise ValidationError(f"{value} is not even")

        def modify_schema(self, field_schema):
            field_schema["multipleOf"] = 2

    class Pair(models.Base):
        number = fields.IntField(validators=Even())

    >>> Pair.to_json_schema()["properties"]["number"]
    {'type': 'number', 'multipleOf': 2}
