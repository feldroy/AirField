"""AirField: field descriptors for Pydantic models."""

from __future__ import annotations

from typing import Any

from pydantic import Field as PydanticField


def AirField(
    default: Any = ...,
    *,
    primary_key: bool = False,
    default_factory: Any = None,
    **kwargs: Any,
) -> Any:
    """Thin wrapper around :func:`pydantic.Field` that accepts a ``primary_key`` flag.

    The flag is stored in ``json_schema_extra`` so ORMs can read it
    when generating SQL.

    Returns:
        A Pydantic FieldInfo with optional ``primary_key`` metadata.
    """
    schema_extra: dict[str, Any] = kwargs.pop("json_schema_extra", None) or {}
    if primary_key:
        schema_extra["primary_key"] = True

    pydantic_kwargs: dict[str, Any] = {**kwargs, "json_schema_extra": schema_extra}
    if default is not ...:
        pydantic_kwargs["default"] = default
    if default_factory is not None:
        pydantic_kwargs["default_factory"] = default_factory

    return PydanticField(**pydantic_kwargs)
