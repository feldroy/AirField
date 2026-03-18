"""AirField: unified field descriptor for Pydantic models.

Wraps pydantic.Field with parameters for database metadata (primary_key)
and UI presentation (type, label, widget, choices, placeholder, help_text,
autofocus). Stores presentation metadata in json_schema_extra so both ORM
and form renderers can read what they need.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field as PydanticField

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

    Extra kwargs that pydantic.Field doesn't recognize are stored in
    ``json_schema_extra`` alongside the presentation metadata.

    Returns:
        A Pydantic FieldInfo configured with all specified parameters.
    """
    schema_extra: dict[str, Any] = kwargs.pop("json_schema_extra", None) or {}

    # Database metadata
    if primary_key:
        schema_extra["primary_key"] = True

    # UI presentation metadata
    if type:
        schema_extra[type] = True
    if label:
        schema_extra["label"] = label
    if widget:
        schema_extra["widget"] = widget
    if choices:
        schema_extra["choices"] = choices
    if autofocus:
        schema_extra["autofocus"] = True
    if placeholder:
        schema_extra["placeholder"] = placeholder
    if help_text:
        schema_extra["help_text"] = help_text

    # Separate pydantic-known kwargs from extras
    pydantic_kwargs: dict[str, Any] = {}
    for key, value in kwargs.items():
        if key in _PYDANTIC_FIELD_PARAMS:
            pydantic_kwargs[key] = value
        else:
            schema_extra[key] = value

    pydantic_kwargs["json_schema_extra"] = schema_extra
    if default is not ...:
        pydantic_kwargs["default"] = default
    if default_factory is not None:
        pydantic_kwargs["default_factory"] = default_factory

    return PydanticField(**pydantic_kwargs)
