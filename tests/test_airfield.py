"""Tests for `airfield` package."""

from __future__ import annotations

from typing import Annotated

import pytest
from pydantic import BaseModel

import airfield
from airfield import (
    AirField,
    BasePresentation,
    Choices,
    HelpText,
    Hidden,
    Label,
    Placeholder,
    ReadOnly,
    Widget,
)


def test_import():
    """Verify the package can be imported."""
    assert airfield


# ---------------------------------------------------------------------------
# Helper to extract typed metadata from a field
# ---------------------------------------------------------------------------


def _get_meta(model: type[BaseModel], field_name: str, meta_type: type):
    """Return the first metadata object of meta_type from a field, or None."""
    field_info = model.model_fields[field_name]
    for m in field_info.metadata:
        if isinstance(m, meta_type):
            return m
    return None


def _get_all_meta(model: type[BaseModel], field_name: str, base: type = BasePresentation):
    """Return all metadata objects that are instances of base."""
    field_info = model.model_fields[field_name]
    return [m for m in field_info.metadata if isinstance(m, base)]


# ---------------------------------------------------------------------------
# AirField produces typed metadata
# ---------------------------------------------------------------------------


class TestAirFieldProducesTypedMetadata:
    """AirField() kwargs should produce typed metadata objects in field_info.metadata."""

    def test_label(self):
        class M(BaseModel):
            name: str = AirField(label="Full Name")

        meta = _get_meta(M, "name", Label)
        assert meta is not None
        assert meta.text == "Full Name"

    def test_widget_from_type_kwarg(self):
        """AirField(type="email") should produce Widget("email")."""

        class M(BaseModel):
            email: str = AirField(type="email")

        meta = _get_meta(M, "email", Widget)
        assert meta is not None
        assert meta.kind == "email"

    def test_widget_from_widget_kwarg(self):
        """AirField(widget="textarea") should produce Widget("textarea")."""

        class M(BaseModel):
            bio: str = AirField(widget="textarea")

        meta = _get_meta(M, "bio", Widget)
        assert meta is not None
        assert meta.kind == "textarea"

    def test_placeholder(self):
        class M(BaseModel):
            email: str = AirField(placeholder="you@example.com")

        meta = _get_meta(M, "email", Placeholder)
        assert meta is not None
        assert meta.text == "you@example.com"

    def test_help_text(self):
        class M(BaseModel):
            password: str = AirField(help_text="At least 8 characters")

        meta = _get_meta(M, "password", HelpText)
        assert meta is not None
        assert meta.text == "At least 8 characters"

    def test_choices(self):
        class M(BaseModel):
            color: str = AirField(choices=[("r", "Red"), ("g", "Green")])

        meta = _get_meta(M, "color", Choices)
        assert meta is not None
        assert meta.options == (("r", "Red"), ("g", "Green"))

    def test_multiple_metadata(self):
        """A field with several kwargs gets multiple typed metadata objects."""

        class M(BaseModel):
            email: str = AirField(type="email", label="Email Address", placeholder="you@example.com")

        all_meta = _get_all_meta(M, "email")
        types = {type(m) for m in all_meta}
        assert types == {Widget, Label, Placeholder}

    def test_no_presentation_metadata_when_none_specified(self):
        class M(BaseModel):
            name: str = AirField()

        all_meta = _get_all_meta(M, "name")
        assert all_meta == []


# ---------------------------------------------------------------------------
# AirField still passes through Pydantic parameters
# ---------------------------------------------------------------------------


class TestAirFieldPydanticPassthrough:
    """Pydantic Field parameters should still work."""

    def test_default_value(self):
        class M(BaseModel):
            name: str = AirField("default_name", label="Name")

        assert M().name == "default_name"
        assert _get_meta(M, "name", Label).text == "Name"

    def test_default_factory(self):
        class M(BaseModel):
            tags: list[str] = AirField(default_factory=list)

        assert M().tags == []

    def test_pydantic_constraints(self):
        class M(BaseModel):
            age: int = AirField(ge=0, le=150)

        with pytest.raises(Exception):
            M(age=-1)
        assert M(age=25).age == 25

    def test_json_schema_extra_passthrough(self):
        """Explicit json_schema_extra should still be set on the field."""

        class M(BaseModel):
            name: str = AirField(json_schema_extra={"x-custom": True})

        field_info = M.model_fields["name"]
        extra = field_info.json_schema_extra
        assert extra is not None
        assert extra["x-custom"] is True

    def test_extra_kwargs_in_json_schema_extra(self):
        """Unknown kwargs should end up in json_schema_extra."""

        class M(BaseModel):
            name: str = AirField(custom_attr="custom_value")

        field_info = M.model_fields["name"]
        assert field_info.json_schema_extra["custom_attr"] == "custom_value"


# ---------------------------------------------------------------------------
# Annotated metadata path produces same result
# ---------------------------------------------------------------------------


class TestAnnotatedMetadata:
    """Annotated[str, Widget("email")] should be discoverable the same way."""

    def test_annotated_widget(self):
        class M(BaseModel):
            email: Annotated[str, Widget("email")]

        meta = _get_meta(M, "email", Widget)
        assert meta is not None
        assert meta.kind == "email"

    def test_annotated_label(self):
        class M(BaseModel):
            name: Annotated[str, Label("Full Name")]

        meta = _get_meta(M, "name", Label)
        assert meta is not None
        assert meta.text == "Full Name"

    def test_annotated_multiple(self):
        class M(BaseModel):
            email: Annotated[str, Widget("email"), Label("Email"), Placeholder("you@example.com")]

        assert _get_meta(M, "email", Widget).kind == "email"
        assert _get_meta(M, "email", Label).text == "Email"
        assert _get_meta(M, "email", Placeholder).text == "you@example.com"

    def test_annotated_hidden(self):
        class M(BaseModel):
            secret: Annotated[str, Hidden("form", "table")]

        meta = _get_meta(M, "secret", Hidden)
        assert meta.in_context("form") is True
        assert meta.in_context("api") is False

    def test_annotated_readonly(self):
        class M(BaseModel):
            created: Annotated[str, ReadOnly("form")]

        meta = _get_meta(M, "created", ReadOnly)
        assert meta.in_context("form") is True
        assert meta.in_context("table") is False


# ---------------------------------------------------------------------------
# Both paths produce equivalent metadata
# ---------------------------------------------------------------------------


class TestBothPathsEquivalent:
    """AirField() and Annotated[] should produce the same metadata."""

    def test_airfield_and_annotated_both_discoverable(self):
        class M(BaseModel):
            email_a: str = AirField(type="email", label="Email")
            email_b: Annotated[str, Widget("email"), Label("Email")]

        # Both should have Widget and Label
        for field_name in ("email_a", "email_b"):
            w = _get_meta(M, field_name, Widget)
            l = _get_meta(M, field_name, Label)
            assert w is not None, f"{field_name} missing Widget"
            assert l is not None, f"{field_name} missing Label"
            assert w.kind == "email"
            assert l.text == "Email"


# ---------------------------------------------------------------------------
# Autofocus (boolean flag, stored in json_schema_extra for now)
# ---------------------------------------------------------------------------


class TestAutofocus:
    """autofocus is a rendering hint, stored in json_schema_extra."""

    def test_autofocus_in_json_schema_extra(self):
        class M(BaseModel):
            name: str = AirField(autofocus=True)

        field_info = M.model_fields["name"]
        extra = field_info.json_schema_extra or {}
        assert extra.get("autofocus") is True

    def test_no_autofocus_by_default(self):
        class M(BaseModel):
            name: str = AirField()

        field_info = M.model_fields["name"]
        extra = field_info.json_schema_extra or {}
        assert "autofocus" not in extra


# ---------------------------------------------------------------------------
# Primary key (database metadata, stored in json_schema_extra)
# ---------------------------------------------------------------------------


class TestPrimaryKey:
    """primary_key is database metadata, stored in json_schema_extra."""

    def test_primary_key_in_json_schema_extra(self):
        class M(BaseModel):
            id: int = AirField(primary_key=True)

        field_info = M.model_fields["id"]
        extra = field_info.json_schema_extra or {}
        assert extra.get("primary_key") is True

    def test_no_primary_key_by_default(self):
        class M(BaseModel):
            id: int = AirField()

        field_info = M.model_fields["id"]
        extra = field_info.json_schema_extra or {}
        assert "primary_key" not in extra
