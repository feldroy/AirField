"""AirField: unified field descriptor for Pydantic models.

Wraps pydantic.Field with parameters for database metadata (primary_key)
and UI presentation (type, label, widget, choices, placeholder, help_text,
autofocus). Stores presentation metadata in json_schema_extra so both ORM
and form renderers can read what they need.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field as PydanticField


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
    # Pydantic pass-through
    default_factory: Any = None,
    **kwargs: Any,
) -> Any:
    """Unified field descriptor for Pydantic models.

    Accepts database metadata (``primary_key``), UI presentation hints
    (``type``, ``label``, ``widget``, ``choices``, ``placeholder``,
    ``help_text``, ``autofocus``), and all standard ``pydantic.Field``
    parameters via ``**kwargs``.

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

    pydantic_kwargs: dict[str, Any] = {**kwargs, "json_schema_extra": schema_extra}
    if default is not ...:
        pydantic_kwargs["default"] = default
    if default_factory is not None:
        pydantic_kwargs["default_factory"] = default_factory

    return PydanticField(**pydantic_kwargs)
