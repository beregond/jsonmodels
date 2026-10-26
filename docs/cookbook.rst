========
Cookbook
========

Short recipes for common tasks.

JSON in, JSON out
-----------------

.. code-block:: python

    import json

    payload = '{"name": "Ann", "address": {"city": "Oslo"}}'

    person = Person(**json.loads(payload))
    person.validate()

    print(json.dumps(person.to_struct()))

`to_struct()` also validates the model, so it raises
:class:`~jsonmodels.errors.ValidationError` for invalid data.

Validating an API payload
-------------------------

.. code-block:: python

    def parse_person(data):
        try:
            person = Person(**data)
            person.validate()
        except (ValidationError, ValueError) as error:
            raise BadRequest(str(error))
        return person

Serving the schema of a model
-----------------------------

.. code-block:: python

    schema = Person.to_json_schema()

It works on the class, no instance needed. Pass it to a JSON schema validator of
your choice to check data outside Python.

Looping over fields
-------------------

Iterating a model gives `(attribute_name, field)` pairs, and the class method
`iterate_with_name` adds the name used in structures:

.. code-block:: python

    >>> for name, field in person:
    ...     print(name, field)
    >>> for attr, struct_name, field in Person.iterate_with_name():
    ...     print(attr, struct_name)

Model inheritance
-----------------

Models can inherit from each other, fields are inherited too:

.. code-block:: python

    class Animal(models.Base):
        name = fields.StringField(required=True)

    class Dog(Animal):
        good_boy = fields.BoolField(default=True)

Optional field with a validator
-------------------------------

.. code-block:: python

    age = fields.IntField(nullable=True, validators=validators.Min(0))

Without `nullable=True` the validator would also run for a missing value
(`None`) and fail.

Client-side validation with a schema served over OPTIONS
--------------------------------------------------------

.. warning::

   This is an unconventional recipe, not a standard or recommended way to build
   APIs. It is shown here because `jsonmodels` makes it cheap to try.

The idea: the server publishes the JSON schema of its models in response to an
HTTP `OPTIONS` request, and the client downloads it and validates the payload
**before** sending it. Invalid data never reaches the server, and the rules live
in one place, the model.

Server (Flask, but any framework works):

.. code-block:: python

    from flask import Flask, jsonify, request
    from jsonmodels import fields, models, validators
    from jsonmodels.errors import ValidationError


    class User(models.Base):
        email = fields.StringField(
            required=True, validators=validators.Regex(r"^[^@]+@[^@]+$")
        )
        age = fields.IntField(
            nullable=True, validators=[validators.Min(0), validators.Max(120)]
        )


    app = Flask(__name__)


    @app.route("/users", methods=["OPTIONS"])
    def users_schema():
        return jsonify(User.to_json_schema())


    @app.route("/users", methods=["POST"])
    def create_user():
        # Never trust the client, validate again.
        try:
            user = User(**request.get_json())
            user.validate()
        except (ValidationError, ValueError) as error:
            return jsonify(error=str(error)), 400
        return jsonify(user.to_struct()), 201

Client (Python, with `requests`, `jsonschema` and `jsonmodels` itself):

.. code-block:: python

    import requests
    from jsonschema import Draft4Validator
    from jsonmodels.utilities import (
        PYTHON_TO_ECMA_FLAGS,
        convert_ecma_regex_to_python,
    )


    def fix_patterns(schema):
        """Turn ECMA-style patterns ("/regex/flags") into plain Python ones."""
        if isinstance(schema, dict):
            if isinstance(schema.get("pattern"), str):
                pattern, flags = convert_ecma_regex_to_python(schema["pattern"])
                inline = "".join(PYTHON_TO_ECMA_FLAGS[flag] for flag in flags)
                schema["pattern"] = f"(?{inline}){pattern}" if inline else pattern
            for value in schema.values():
                fix_patterns(value)
        elif isinstance(schema, list):
            for item in schema:
                fix_patterns(item)
        return schema


    def create_user(base_url, payload):
        schema = fix_patterns(requests.options(f"{base_url}/users").json())
        errors = sorted(Draft4Validator(schema).iter_errors(payload), key=str)
        if errors:
            raise ValueError([error.message for error in errors])
        return requests.post(f"{base_url}/users", json=payload)

.. code-block:: python

    >>> create_user("http://localhost:5000", {"email": "nope"})
    ValueError: ["'nope' does not match '^[^@]+@[^@]+$'"]
    >>> create_user("http://localhost:5000", {"email": "a@b.c", "age": 999})
    ValueError: ['999 is greater than the maximum of 120']

Things to know:

* **Custom validators are invisible to the client.** Only validators that
  modify the schema (all built-in ones, and custom ones with a
  `modify_schema` method, see :doc:`validators`) are enforced by the client.
  Plain functions and validators without `modify_schema` still run on the
  server, but the client will happily send data they would reject. Always keep
  server-side validation.
* **Patterns need fixing.** `Regex` writes patterns in the ECMA form
  (`"/^a/i"`), which generic validators take literally. That is what
  `fix_patterns` above is for, it uses
  :func:`jsonmodels.utilities.convert_ecma_regex_to_python`. A non-Python
  client has to do the same by hand, e.g. in JavaScript with
  `new RegExp(body, flags)`.
* **The schema follows JSON schema draft 4** (boolean `exclusiveMinimum` and
  `exclusiveMaximum`), so use `Draft4Validator`.
* **Browsers use `OPTIONS` for CORS preflight.** If the API is called from a
  browser on another origin, your `OPTIONS` handler must keep answering
  preflight requests correctly (with the right `Access-Control-*` headers), or
  you should serve the schema from a separate URL.
* Cache the schema on the client, it changes only when the server is deployed.

Migrating
---------

* **2.9** drops Python 3.10 and adds 3.15.
* **2.8** drops PyPy and Python 3.8 and 3.9.
* `structue_name` (a typo) is deprecated in favor of `structure_name` and will
  be removed in 3.0.

See :doc:`history` for the full list.
