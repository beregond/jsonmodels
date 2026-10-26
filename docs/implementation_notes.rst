====================
Implementation notes
====================

Below you can read some implementation specific quirks you should know/remember
about when you are using `jsonmodels` (especially on production
servers/applications).

Where values are stored
-----------------------

Fields are descriptors that live on the model class, so the values of all
instances are kept in the field, in a `WeakKeyDictionary` keyed by an internal
per-instance key. When a model instance is garbage collected, its values are
dropped with it.

Lists are validated lazily
--------------------------

A `ListField` that was never assigned is a
:class:`~jsonmodels.collections.ModelCollection`, which validates each item on
`append` and item assignment.

After you assign a whole list (`model.items = [...]`), the stored value is a
plain `list`. Later `append` calls are not checked, but the model is still
validated by `validate()`, `to_struct()` and `to_json_schema()`.

Validation of missing values
----------------------------

Unset fields read as `None` (or their default), and validators run on that
value unless the field is `nullable=True`.

Deprecations
------------

`BaseField.structue_name` is a misspelled alias of `structure_name`. It emits
`DeprecationWarning` and will be removed in version 3.0.
