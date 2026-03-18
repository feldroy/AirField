# Usage

## The convenience function

`AirField()` wraps `pydantic.Field()` with presentation parameters. Each one becomes a typed metadata object in `field_info.metadata`.

!!! note
    AirField works with any Pydantic `BaseModel`. If you're using [Air](https://github.com/feldroy/air), use `AirModel` instead, which extends BaseModel with ORM and form support.

```python
from pydantic import BaseModel
from airfield import AirField

class Article(BaseModel):
    id: int = AirField(primary_key=True)
    title: str = AirField(label="Title", autofocus=True)
    email: str = AirField(type="email", label="Email Address")
    body: str = AirField(widget="textarea", placeholder="Write something...")
    status: str = AirField(choices=[("draft", "Draft"), ("published", "Published")])
```

Pydantic parameters pass straight through:

```python
class ContactForm(BaseModel):
    name: str = AirField(label="Full Name", min_length=2, max_length=100)
    age: int = AirField(label="Age", ge=0, le=150)
```

## The Annotated path

For composability or when you don't need `AirField()`, use the types directly in `Annotated`:

```python
from typing import Annotated
from pydantic import BaseModel
from airfield import Widget, Label, Placeholder, PrimaryKey, Autofocus

class Article(BaseModel):
    id: Annotated[int, PrimaryKey()]
    title: Annotated[str, Label("Title"), Autofocus()]
    email: Annotated[str, Widget("email"), Label("Email Address")]
    body: Annotated[str, Widget("textarea"), Placeholder("Write something...")]
```

Both paths produce identical metadata. One `isinstance` loop finds everything regardless of how the field was declared.

## Reading metadata

Consumers traverse `field_info.metadata` with `isinstance` checks, the same way Pydantic discovers `annotated-types` constraints:

```python
from airfield import BasePresentation, Widget, Label, PrimaryKey, Autofocus

for name, field_info in MyModel.model_fields.items():
    for m in field_info.metadata:
        if isinstance(m, Widget):
            print(f"{name}: widget={m.kind}")
        elif isinstance(m, Label):
            print(f"{name}: label={m.text}")
        elif isinstance(m, PrimaryKey):
            print(f"{name}: is primary key")
        elif isinstance(m, Autofocus):
            print(f"{name}: gets focus")
```

To find all AirField metadata at once:

```python
presentation = [m for m in field_info.metadata if isinstance(m, BasePresentation)]
```

## Presentation types

Every type is a frozen dataclass with `__slots__`, inheriting from `BasePresentation`.

### Identity

- **`PrimaryKey()`** -- marks the field as the record identity. Affects presentation: typically hidden in create forms, read-only in edit forms, displayed as a link in tables.

### Labeling

- **`Label(text)`** -- human-readable display name for forms, tables, CLI prompts, chart axes.
- **`Placeholder(text)`** -- hint text shown when the field is empty.
- **`HelpText(text)`** -- explanatory text below the input, in tooltips, or in CLI help.

### Input and display

- **`Widget(kind)`** -- preferred input mechanism. Standard kinds: `text`, `textarea`, `date`, `datetime`, `time`, `color`, `email`, `url`, `password`, `file`, `hidden`, `toggle`, `slider`, `rating`, `rich_text`, `code`, `search`, `phone`, `currency`, `autocomplete`. Unknown kinds fall back to `"text"`.
- **`DisplayFormat(pattern, locale=None)`** -- how to format the value for display: `"percent"`, `"currency"`, `"bytes"`, `"relative_time"`, or a strftime pattern.
- **`Choices(*options)`** -- constrains to labeled options. Each option is `(value, display_label)`.

### Focus

- **`Autofocus()`** -- this field receives input focus when the UI loads. Only one field per form/view should have this.

### Visibility and editability

- **`Hidden(*contexts)`** -- field is not shown in the specified contexts (`"form"`, `"table"`, `"detail"`, `"api"`, `"cli"`, `"export"`). With no arguments, hidden everywhere.
- **`ReadOnly(*contexts)`** -- field is displayed but not editable. With no arguments, read-only everywhere.

### Tables and lists

- **`ColumnAlign(align)`** -- `"left"`, `"center"`, or `"right"` alignment in table columns.
- **`ColumnWidth(weight=1.0, min_chars=None, max_chars=None)`** -- relative width in tables. Weight=2 gets roughly twice the space of weight=1.
- **`Filterable(kind="exact")`** -- field appears in search/filter UI. Kinds: `"exact"`, `"contains"`, `"range"`, `"multi_select"`.
- **`Sortable(default=False, descending=False)`** -- field is sortable. When `default=True`, this is the initial sort key.

### Layout and priority

- **`Grouped(name, order=0)`** -- assigns to a named group (fieldset in forms, section in detail views).
- **`Priority(level)`** -- importance relative to siblings. Higher priority fields are shown first or shown when space is limited.
- **`Compact(format=None, max_length=None)`** -- how to represent in space-constrained contexts.
