# AirField

AirField is a presentation metadata vocabulary for Pydantic model fields. It tells downstream consumers (form renderers, table builders, CLI generators, API docs) *how* to present a field without rendering anything itself. Think of it as the complement to annotated-types: annotated-types is for validation, AirField is for presentation.

AirField works with any Pydantic `BaseModel`. It has no dependency on Air, AirModel, or AirForm. The relationship is one-way: those packages depend on AirField.

## Two Declaration Paths (Same Result)

### AirField() convenience function

```python
from pydantic import BaseModel
from airfield import AirField

class User(BaseModel):
    name: str = AirField(label="Full Name", placeholder="Jane Doe")
    email: str = AirField(type="email", label="Email", autofocus=True)
    role: str = AirField(choices=[("admin", "Admin"), ("user", "User")])
    bio: str = AirField(widget="textarea", help_text="Tell us about yourself")
```

`AirField()` is a function (PascalCase by design). It calls `pydantic.Field()` internally and appends typed metadata objects to `field_info.metadata`. All standard Pydantic Field parameters (`default`, `default_factory`, `min_length`, `max_length`, `ge`, `le`, `pattern`, etc.) pass through.

### Annotated[] metadata

```python
from typing import Annotated
from pydantic import BaseModel
from airfield import Widget, Label, Placeholder, Autofocus

class User(BaseModel):
    name: Annotated[str, Label("Full Name"), Placeholder("Jane Doe")]
    email: Annotated[str, Widget("email"), Label("Email"), Autofocus()]
```

Both paths produce identical metadata in `field_info.metadata`. Use whichever reads better for your case. The `AirField()` function is more compact when setting multiple presentation attributes; `Annotated[]` is clearer when mixing with validation constraints from annotated-types.

You can combine both on the same field. Use `Annotated[]` for types that don't have `AirField()` shortcuts (like `Grouped`, `CsrfToken`, `Hidden`) and `AirField()` for the rest:

```python
phone: Annotated[str | None, Grouped("contact_info")] = AirField(
    default=None, widget="phone", label="Phone"
)
```

## All Presentation Types

Every type is a frozen dataclass inheriting from `BasePresentation`. All are importable from `airfield`.

### Markers (no fields)

| Type | Purpose |
|---|---|
| `PrimaryKey()` | Field is the record identity |
| `CsrfToken()` | CSRF protection token, rendered as hidden input |
| `Autofocus()` | Field receives initial focus |

### Text metadata

| Type | Fields | Example |
|---|---|---|
| `Label(text)` | `text: str` | `Label("Email Address")` |
| `Placeholder(text)` | `text: str` | `Placeholder("you@example.com")` |
| `HelpText(text)` | `text: str` | `HelpText("We'll never share your email")` |
| `Widget(kind)` | `kind: str` | `Widget("textarea")`, `Widget("email")`, `Widget("select")` |

### Display and layout

| Type | Fields | Example |
|---|---|---|
| `DisplayFormat(pattern, locale=None)` | `pattern: str`, `locale: str \| None` | `DisplayFormat("${:,.2f}")` |
| `ColumnAlign(align)` | `align: Literal["left", "center", "right"]` | `ColumnAlign("right")` |
| `ColumnWidth(weight=1.0, min_chars=None, max_chars=None)` | `weight: float`, `min_chars: int \| None`, `max_chars: int \| None` | `ColumnWidth(weight=2.0, min_chars=10)` |
| `Grouped(name, order=0)` | `name: str`, `order: int` | `Grouped("contact_info", order=1)` |
| `Priority(level)` | `level: int` | `Priority(1)` |
| `Compact(format=None, max_length=None)` | `format: str \| None`, `max_length: int \| None` | `Compact(max_length=50)` |

### Choices

```python
Choices(("admin", "Admin"), ("user", "User"), ("guest", "Guest"))
```

Takes `*options` (not a list). Each option is a `(value, label)` tuple. Stored as `options: tuple[tuple[Any, str], ...]`.

When `AirField(choices=...)` is used without `type` or `widget`, it automatically appends `Widget(kind="select")`.

### Context-aware visibility

```python
Hidden("form", "table")       # hidden in "form" and "table" contexts
ReadOnly("edit")              # read-only in "edit" context

hidden.in_context("form")    # True
hidden.in_context("api")     # False
```

Both take `*contexts` and store them as `contexts: tuple[str, ...]`. The `in_context(ctx)` method checks membership.

### Table behavior

| Type | Fields | Example |
|---|---|---|
| `Filterable(kind="exact")` | `kind: Literal["exact", "contains", "range", "multi_select"]` | `Filterable("contains")` |
| `Sortable(default=False, descending=False)` | `default: bool`, `descending: bool` | `Sortable(default=True)` |

## Discovering Metadata

Consumers find metadata with `isinstance` checks on `field_info.metadata`, the same pattern Pydantic uses for annotated-types constraints:

```python
from pydantic import BaseModel
from airfield import Label, Widget, BasePresentation

class User(BaseModel):
    email: str = AirField(type="email", label="Email")

field_info = User.model_fields["email"]

# Find a specific type
label = next((m for m in field_info.metadata if isinstance(m, Label)), None)
if label:
    print(label.text)  # "Email"

# Find all presentation metadata
presentation = [m for m in field_info.metadata if isinstance(m, BasePresentation)]
```

AirField never writes to `json_schema_extra`. All metadata lives in `field_info.metadata` as typed objects.

## AirField() Parameter Reference

```python
AirField(
    default=...,              # passed to pydantic.Field()
    *,
    primary_key: bool = False,            # -> PrimaryKey()
    type: str | None = None,              # -> Widget(kind=type), alias for widget
    label: str | None = None,             # -> Label(text=label)
    widget: str | None = None,            # -> Widget(kind=widget)
    choices: list[tuple[Any, str]] | None = None,  # -> Choices(*choices), auto-adds Widget("select")
    autofocus: bool = False,              # -> Autofocus()
    placeholder: str | None = None,       # -> Placeholder(text=placeholder)
    help_text: str | None = None,         # -> HelpText(text=help_text)
    default_factory=None,     # passed to pydantic.Field()
    **kwargs,                 # passed to pydantic.Field()
)
```

`type` and `widget` both produce `Widget(kind=...)`. Use `type` for semantic input types (`"email"`, `"password"`, `"date"`), `widget` for explicit UI controls (`"textarea"`, `"select"`, `"checkbox"`).

## Build and Test

Requires: Python 3.12+ (see CI workflow for tested versions)

```bash
uv run pytest              # run tests
just qa                    # format + lint + typecheck + test
just test                  # tests only
just testall               # tests on all Python versions
just type-check            # ty type checker
just coverage              # coverage across all versions
```

## Dependencies

Runtime: `pydantic` (the only one).

```toml
[project]
dependencies = ["airfield"]
```

## Project Structure

```
src/airfield/
    __init__.py     # public API, re-exports all types + AirField
    __main__.py     # stub (python -m airfield)
    main.py         # AirField() convenience function
    types.py        # frozen dataclass types + BasePresentation
    cli.py          # stub (future: airfield inspect)
    utils.py        # stub (future: metadata extraction helpers)
    py.typed        # PEP 561 marker
tests/
    test_airfield.py
```
