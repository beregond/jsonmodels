=======================
Embedded models & lists
=======================

Models can contain other models and lists of them.

EmbeddedField
-------------

.. code-block:: python

    class Address(models.Base):
        city = fields.StringField(required=True)

    class Person(models.Base):
        name = fields.StringField()
        address = fields.EmbeddedField(Address)

Embedded values can be given as model instances or as plain dicts, which are
turned into models for you:

.. code-block:: python

    >>> person = Person(name="Ann", address={"city": "Oslo"})
    >>> person.address.city
    'Oslo'
    >>> person.to_struct()
    {'address': {'city': 'Oslo'}, 'name': 'Ann'}

Validation goes through nested models, and errors name each level:

.. code-block:: python

    >>> Person(address={}).validate()
    *** ValidationError: Error for field 'address': ("Error for field 'city'.", ValidationError('Field is required!'))

Several allowed types
---------------------

Both :class:`~jsonmodels.fields.EmbeddedField` and
:class:`~jsonmodels.fields.ListField` take a list of allowed models:

.. code-block:: python

    class Zoo(models.Base):
        star = fields.EmbeddedField([Cat, Dog])
        animals = fields.ListField([Cat, Dog])

With more than one type, `jsonmodels` can't guess which one a plain dict should
become, so a `ValidationError` ("Cannot decide which type to choose")
is raised. Pass real instances (`Zoo(animals=[Cat(...), Dog(...)])`)
in that case.

ListField
---------

.. code-block:: python

    class Team(models.Base):
        members = fields.ListField(Person)
        nicknames = fields.ListField(str)

* `items_types` can be a single type, or a list of types. Without it, any item
  is accepted.
* A `ListField` is never required, and is an empty list by default.
* Use `validators` for the list as a whole (e.g. its length) and
  `item_validators` for each item, see :doc:`validators`.
* Dicts in a list of one model type are turned into models.

Self references and lazy types
------------------------------

A class can't refer to itself in its own body, so give the type as a string:

.. code-block:: python

    class Node(models.Base):
        value = fields.IntField()
        parent = fields.EmbeddedField("Node")
        children = fields.ListField(["Node"])

    >>> tree = Node(value=1, children=[{"value": 2}, {"value": 3}])

Strings are resolved when the field is first used, relative to the module of
the model that owns the field:

* `"Node"` or `".Node"`: a class in the same module.
* `"pkg.other.Node"`: a class in another module (absolute path).
* `"..other.Node"`: relative to the package of the current module (a sibling
  module). Each additional dot goes one package up (`"...other.Node"`).

This also works for models defined later in the same module, and for circular
references between modules.

Schemas for self-referencing models use JSON schema `definitions`, see
:ref:`json-schema`.
