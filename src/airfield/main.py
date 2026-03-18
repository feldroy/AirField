"""AirField: unified field descriptor for Pydantic models.

Wraps pydantic.Field with parameters for database metadata (primary_key)
and UI presentation (type, label, widget, choices, placeholder, help_text,
autofocus). Stores presentation metadata as typed objects in
field_info.metadata so consumers can discover them with isinstance checks,
the same way Pydantic discovers annotated-types constraints.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field as PydanticField
from pydantic.fields import FieldInfo

from airfield.types import Choices, HelpText, Label, Placeholder, Widget

# Parameters that pydantic.Field accepts (so we know which **kwargs to forward
# vs. which to stuff into json_schema_extra as extra metadata).
_PYDANTIC_FIELD_PARAMS = frozenset({
    "default_factory", "alias", "alias_priority", "validation_alias",
    "serialization_alias", "title", "field_title_generator", "description",
    "examples", "exclude", "exclude_if", "discriminator", "deprecated",
    "json_schema_extra", "frozen", "validate_default", "repr", "init",
    "init_var", "kw_only", "pattern", "strict", "coerce_numbers_to_str",
    "gt", "ge", "lt", "le", "multiple_of", "allow_inf_nan", "max_digits",
    "decimal_places", "min_length", "max_length", "union_mode", "fail_fast",
})


def AirField(  # noqa: N802
    default: Any = ...,
    *,
    # Database
    primary_key: bool = False,
    # Form rendering / UI presentation
    type: str | None = None,
    label: str | None = None,
    widget: str | None = None,
    choices: list[tuple[Any, str]] | None = None,
    autofocus: bool = False,
    placeholder: str | None = None,
    help_text: str | None = None,
    # Pydantic pass-through + extra kwargs
    default_factory: Any = None,
    **kwargs: Any,
) -> Any:
    """Unified field descriptor for Pydantic models.

    Accepts database metadata (``primary_key``), UI presentation hints
    (``type``, ``label``, ``widget``, ``choices``, ``placeholder``,
    ``help_text``, ``autofocus``), all standard ``pydantic.Field``
    parameters, and arbitrary extra keyword arguments.

    Presentation kwargs become typed metadata objects in
    ``field_info.metadata`` (Widget, Label, etc.). Database and
    rendering-specific flags (primary_key, autofocus) go into
    ``json_schema_extra``. Extra kwargs that pydantic.Field doesn't
    recognize also go into ``json_schema_extra``.

    Returns:
        A Pydantic FieldInfo configured with all specified parameters.
    """
    schema_extra: dict[str, Any] = kwargs.pop("json_schema_extra", None) or {}

    # Database metadata
    if primary_key:
        schema_extra["primary_key"] = True

    # Rendering-specific flags (not presentation metadata)
    if autofocus:
        schema_extra["autofocus"] = True

    # Separate pydantic-known kwargs from extras
    pydantic_kwargs: dict[str, Any] = {}
    for key, value in kwargs.items():
        if key in _PYDANTIC_FIELD_PARAMS:
            pydantic_kwargs[key] = value
        else:
            schema_extra[key] = value

    if schema_extra:
        pydantic_kwargs["json_schema_extra"] = schema_extra
    if default is not ...:
        pydantic_kwargs["default"] = default
    if default_factory is not None:
        pydantic_kwargs["default_factory"] = default_factory

    field_info: FieldInfo = PydanticField(**pydantic_kwargs)

    # Build typed presentation metadata
    if type:
        field_info.metadata.append(Widget(kind=type))
    if widget:
        field_info.metadata.append(Widget(kind=widget))
    if label:
        field_info.metadata.append(Label(text=label))
    if placeholder:
        field_info.metadata.append(Placeholder(text=placeholder))
    if help_text:
        field_info.metadata.append(HelpText(text=help_text))
    if choices:
        field_info.metadata.append(Choices(*choices))

    return field_info
