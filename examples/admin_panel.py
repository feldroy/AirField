"""
AirField admin models for a SaaS admin panel.

Three models:
  - Product   (e-commerce catalog)
  - UserProfile (user management)

Plus render_table_headers(), a metadata consumer that builds ordered column
descriptor dicts from any BaseModel class.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel

from airfield import (
    AirField,
    Autofocus,
    BasePresentation,
    Choices,
    ColumnAlign,
    ColumnWidth,
    Compact,
    DisplayFormat,
    Filterable,
    Grouped,
    HelpText,
    Hidden,
    Label,
    Priority,
    PrimaryKey,
    ReadOnly,
    Sortable,
    Widget,
)


# ---------------------------------------------------------------------------
# 1. Product
# ---------------------------------------------------------------------------

class Product(BaseModel):
    # primary key — AirField(primary_key=True) appends PrimaryKey() internally.
    id: int = AirField(primary_key=True)

    # Labeled, autofocused, sortable by default, filterable by contains.
    # Sortable and Filterable have no AirField() shortcuts, so they go in
    # Annotated[].
    name: Annotated[str, Sortable(default=True), Filterable("contains")] = AirField(
        label="Name",
        autofocus=True,
    )

    # Textarea widget with compact rendering (truncate at 80 chars in tables).
    # Compact has no AirField() shortcut.
    description: Annotated[str, Compact(max_length=80)] = AirField(
        widget="textarea",
        label="Description",
    )

    # Float, currency display, right-aligned, range-filterable, weight 1.5.
    # DisplayFormat / ColumnAlign / ColumnWidth / Filterable all go in
    # Annotated[] — none are AirField() shortcuts.
    price: Annotated[
        float,
        DisplayFormat("${:,.2f}"),
        ColumnAlign("right"),
        ColumnWidth(weight=1.5),
        Filterable("range"),
    ] = AirField(label="Price")

    # Choices select; help text explains effect on search placement.
    category: str = AirField(
        label="Category",
        choices=[
            ("electronics", "Electronics"),
            ("clothing", "Clothing"),
            ("books", "Books"),
            ("food", "Food"),
        ],
        help_text="Category affects search placement and browse visibility.",
    )

    # Hidden in create forms; read-only when shown in table context.
    status: Annotated[str, Hidden("create"), ReadOnly("table")] = AirField(
        label="Status",
        choices=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("archived", "Archived"),
        ],
    )

    # Hidden from API and export contexts entirely; textarea widget.
    internal_notes: Annotated[str, Hidden("api", "export")] = AirField(
        widget="textarea",
        label="Internal Notes",
        default="",
    )

    # Datetime, read-only everywhere (create + edit + table), default-sorted,
    # displayed as relative time.
    # NOTE: "relative" is a guess for the DisplayFormat pattern — the doc shows
    # a format-string example ("${:,.2f}") but does not document a canonical
    # token for relative time. A real renderer would need to agree on this
    # convention.
    created_at: Annotated[
        str,
        ReadOnly("create", "edit", "table"),
        Sortable(default=True),
        DisplayFormat("relative"),
    ] = AirField(
        type="datetime",
        label="Created At",
    )


# ---------------------------------------------------------------------------
# 2. UserProfile
# ---------------------------------------------------------------------------

class UserProfile(BaseModel):
    # Primary key.
    id: int = AirField(primary_key=True)

    # Email widget, labeled, exact-filterable, top priority.
    email: Annotated[str, Filterable("exact"), Priority(1)] = AirField(
        type="email",
        label="Email",
    )

    # Display name, labeled, sortable, second priority.
    display_name: Annotated[str, Sortable(), Priority(2)] = AirField(
        label="Display Name",
    )

    # Role with multi-select filter.
    role: Annotated[str, Filterable("multi_select")] = AirField(
        label="Role",
        choices=[
            ("admin", "Admin"),
            ("editor", "Editor"),
            ("viewer", "Viewer"),
        ],
    )

    # Avatar URL — hidden in tables, grouped under "appearance".
    avatar_url: Annotated[str, Hidden("table"), Grouped("appearance")] = AirField(
        type="url",
        label="Avatar URL",
        default="",
    )

    # Bio — textarea, compact to 50 chars, grouped under "appearance" (order 2).
    bio: Annotated[str, Compact(max_length=50), Grouped("appearance", order=2)] = AirField(
        widget="textarea",
        label="Bio",
        default="",
    )

    # Verified flag — grouped under "status", constrained column width.
    is_verified: Annotated[
        bool,
        Grouped("status"),
        ColumnWidth(min_chars=5, max_chars=10),
    ] = AirField(label="Verified", default=False)

    # Last login — datetime, read-only, default-sorted descending, relative time.
    last_login: Annotated[
        str | None,
        ReadOnly("create", "edit", "table"),
        Sortable(default=True, descending=True),
        DisplayFormat("relative"),
    ] = AirField(type="datetime", label="Last Login", default=None)


# ---------------------------------------------------------------------------
# 3. render_table_headers
# ---------------------------------------------------------------------------

def render_table_headers(model: type[BaseModel]) -> list[dict[str, Any]]:
    """Return ordered column descriptor dicts for visible table columns.

    Fields hidden in the "table" context (via Hidden("table", ...)) are
    excluded entirely.

    Ordering: Priority(level) fields come first (higher level = earlier),
    then remaining fields in declaration order.

    Each dict:
        name          field name
        label         Label.text, falling back to the field name
        align         ColumnAlign.align, defaulting to "left"
        sortable      bool from Sortable metadata (False if absent)
        filterable    Filterable.kind if present, else None
        width_weight  ColumnWidth.weight, defaulting to 1.0
    """
    columns: list[dict[str, Any]] = []

    for field_name, field_info in model.model_fields.items():
        meta: list[Any] = field_info.metadata

        # --- visibility check ---
        hidden = next((m for m in meta if isinstance(m, Hidden)), None)
        if hidden is not None and hidden.in_context("table"):
            continue

        # --- extract typed metadata ---
        label_obj = next((m for m in meta if isinstance(m, Label)), None)
        align_obj = next((m for m in meta if isinstance(m, ColumnAlign)), None)
        sortable_obj = next((m for m in meta if isinstance(m, Sortable)), None)
        filterable_obj = next((m for m in meta if isinstance(m, Filterable)), None)
        width_obj = next((m for m in meta if isinstance(m, ColumnWidth)), None)
        priority_obj = next((m for m in meta if isinstance(m, Priority)), None)

        columns.append(
            {
                "name": field_name,
                "label": label_obj.text if label_obj is not None else field_name,
                "align": align_obj.align if align_obj is not None else "left",
                "sortable": sortable_obj is not None,
                "filterable": filterable_obj.kind if filterable_obj is not None else None,
                "width_weight": width_obj.weight if width_obj is not None else 1.0,
                # _priority is a sort key only; stripped before returning
                "_priority": priority_obj.level if priority_obj is not None else None,
            }
        )

    # Sort: fields with Priority come first (highest level first), then
    # declaration-order fields (stable sort preserves their relative order).
    # Python's sort is stable, so we can sort once with a composite key:
    #   (0, -level) for Priority fields  →  sort to front, highest first
    #   (1, 0)      for unprioritized    →  maintain declaration order
    columns.sort(
        key=lambda c: (0, -(c["_priority"])) if c["_priority"] is not None else (1, 0)
    )

    # Strip internal sort key before returning.
    for col in columns:
        del col["_priority"]

    return columns
