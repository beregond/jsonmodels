from jsonmodels import fields, models


class Child(models.Base):
    name = fields.StringField()


class Parent(models.Base):
    child = fields.EmbeddedField(Child)
    data = fields.DictField()


class CustomChild(models.Base):
    __schema_title__ = "Custom Child"

    name = fields.StringField()


class CustomParent(models.Base):
    __schema_title__ = "Custom Parent"

    child = fields.EmbeddedField(CustomChild)


class InheritingChild(CustomChild):
    pass


class ResetChild(CustomChild):
    __schema_title__ = "Reset"


class Node(models.Base):
    __schema_title__ = "Custom Node"

    other = fields.EmbeddedField("Other")


class Other(models.Base):
    node = fields.EmbeddedField(Node)


class PlainSchemaTitle(models.Base):
    schema_title = fields.StringField()


class NullableParent(models.Base):
    child = fields.EmbeddedField(Child, nullable=True)


def test_default_title_is_class_name():
    assert Child.to_json_schema()["title"] == "Child"


def test_title_on_nested_object():
    schema = Parent.to_json_schema()

    assert schema["title"] == "Parent"
    assert schema["properties"]["child"]["title"] == "Child"


def test_dict_field_has_no_title():
    assert "title" not in Parent.to_json_schema()["properties"]["data"]


def test_dunder_schema_title_overrides_default():
    schema = CustomParent.to_json_schema()

    assert schema["title"] == "Custom Parent"
    assert schema["properties"]["child"]["title"] == "Custom Child"


def test_dunder_schema_title_is_not_a_field():
    assert "__schema_title__" not in dict(CustomParent.iterate_over_fields())
    assert "__schema_title__" not in CustomParent.to_json_schema()["properties"]


def test_dunder_schema_title_is_inherited():
    assert InheritingChild.to_json_schema()["title"] == "Custom Child"
    assert ResetChild.to_json_schema()["title"] == "Reset"


def test_plain_schema_title_field_does_not_affect_title():
    schema = PlainSchemaTitle.to_json_schema()

    assert schema["title"] == "PlainSchemaTitle"
    assert "schema_title" in schema["properties"]
    assert "__schema_title__" not in schema["properties"]


def test_title_in_definitions():
    schema = Node.to_json_schema()

    assert schema["title"] == "Custom Node"
    titles = {name: d["title"] for name, d in schema["definitions"].items()}
    assert titles == {
        "tests_test_title_node": "Custom Node",
        "tests_test_title_other": "Other",
    }


def test_nullable_embedded_title():
    object_branch, null_branch = NullableParent.to_json_schema()["properties"]["child"][
        "oneOf"
    ]

    assert object_branch["title"] == "Child"
    assert "title" not in null_branch
