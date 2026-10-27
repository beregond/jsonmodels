===============
Error handling
===============

All exceptions live in :mod:`jsonmodels.errors`.

ValidationError
---------------

Raised when a value is invalid, which happens:

* when a value is assigned to a field (including in the constructor and
  :meth:`~jsonmodels.models.Base.populate`),
* when a required field is read without a value,
* when :meth:`~jsonmodels.models.Base.validate`, `to_struct()` or
  `to_json_schema()` are called.

Errors from validators on nested models are wrapped with the name of each
field, so you can see where the problem is:

.. code-block:: python

    >>> from jsonmodels.errors import ValidationError
    >>> try:
    ...     Person(name="Ann", address={}).validate()
    ... except ValidationError as error:
    ...     print(error)
    Error for field 'address': ("Error for field 'city'.", ValidationError('Field is required!'))

Casting problems from `IntField` (e.g. `"abc"`) or from the date fields
(an unparsable string) are not wrapped, so they surface as `ValueError`
(or `dateutil` errors, which are `ValueError` subclasses).

If you validate incoming data, catch both:

.. code-block:: python

    try:
        model = Person(**payload)
        model.validate()
    except (ValidationError, ValueError) as error:
        ...  # respond with 400

FieldNotFound
-------------

Raised by :meth:`~jsonmodels.models.Base.get_field` when the model has no
field with that attribute name.

FieldNotSupported
-----------------

Raised while building a JSON schema (:ref:`json-schema`), when a field
type can't be described by it.

Unknown keys
------------

Keys that don't match any field are silently ignored when creating or
populating a model:

.. code-block:: python

    >>> Person(name="Ann", unknown=1).name
    'Ann'
