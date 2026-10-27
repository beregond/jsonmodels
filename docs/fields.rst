===============
Fields overview
===============

Every attribute of a model is a *field*, an instance of a class from
:mod:`jsonmodels.fields`. This page lists all of them and the options they
share.

Available fields
----------------

.. list-table::
   :header-rows: 1
   :widths: 22 22 56

   * - Field
     - Python type
     - Notes
   * - :class:`~jsonmodels.fields.StringField`
     - `str`
     -
   * - :class:`~jsonmodels.fields.IntField`
     - `int`
     - Values are cast with `int()`, so `"5"` becomes `5`.
   * - :class:`~jsonmodels.fields.FloatField`
     - `float` or `int`
     - Not cast, but integers are accepted.
   * - :class:`~jsonmodels.fields.BoolField`
     - `bool`
     - Values are cast with `bool()`.
   * - :class:`~jsonmodels.fields.DictField`
     - `dict`
     - Content of the dictionary is not validated.
   * - :class:`~jsonmodels.fields.ListField`
     - `list`
     - See :doc:`embedded`.
   * - :class:`~jsonmodels.fields.EmbeddedField`
     - another model
     - See :doc:`embedded`.
   * - :class:`~jsonmodels.fields.DateField`
     - `datetime.date`
     - Serialized as `YYYY-MM-DD` by default.
   * - :class:`~jsonmodels.fields.TimeField`
     - `datetime.time`
     - Serialized as ISO 8601 by default.
   * - :class:`~jsonmodels.fields.DateTimeField`
     - `datetime.datetime`
     - Serialized as ISO 8601 by default.

Common options
--------------

All fields accept these keyword arguments:

`required`
    If `True`, a missing value (`None`) raises
    :class:`~jsonmodels.errors.ValidationError`. Default: `False`.

`nullable`
    If `True`, `None` is accepted and skips custom validators. It also makes
    the generated schema accept `null`. Default: `False`.

`default`
    Value used when none was given, also shown in the generated schema. See
    :ref:`default-values`.

`validators`
    A single validator or a list of them. See :doc:`validators`.

`help_text`
    Free-form description of the field. It is not used for validation.

`name`
    Name of the field in structures (dicts, JSON, schema), if it should differ
    from the attribute name. See :ref:`different-names`.

.. note::

   Validators also run when the value is `None`, so a validator like
   :class:`~jsonmodels.validators.Min` on an optional field will fail for a
   missing value. Use `nullable=True` on such fields.

Dates and times
---------------

:class:`~jsonmodels.fields.DateField`, :class:`~jsonmodels.fields.TimeField`
and :class:`~jsonmodels.fields.DateTimeField` accept either real
`datetime` objects or strings (parsed with `dateutil`), and are written back
as strings.

Use `str_format` (a `strftime` format) to change the output:

.. code-block:: python

    class Event(models.Base):
        starts = fields.DateTimeField()
        day = fields.DateField(str_format="%d.%m.%Y")
        at = fields.TimeField()

    >>> event = Event(starts="2024-01-02T03:04:05", day="2024-01-02", at="10:20")
    >>> event.day
    datetime.date(2024, 1, 2)
    >>> event.to_struct()
    {'at': '10:20:00', 'day': '02.01.2024', 'starts': '2024-01-02T03:04:05'}

`str_format` only affects output. Parsing is always done by `dateutil`.

Booleans and numbers
--------------------

.. code-block:: python

    class Item(models.Base):
        count = fields.IntField()
        price = fields.FloatField()
        active = fields.BoolField()

    >>> item = Item(count="3", price=2, active=1)
    >>> item.count, item.price, item.active
    (3, 2, True)

Beware that `BoolField` casts with `bool()`, so the string `"false"` becomes
`True`. Parse such strings yourself before passing them to the model.
