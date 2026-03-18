# AirField

![PyPI version](https://img.shields.io/pypi/v/AirField.svg)

Dataclasses that describe how Pydantic model fields should be presented in any UI context: web forms, CLI prompts, data tables, notebooks, API docs, charts.

* GitHub: https://github.com/feldroy/AirField/
* PyPI package: https://pypi.org/project/AirField/
* Created by: **[Audrey M. Roy Greenfeld](https://audrey.feldroy.com/)** | GitHub https://github.com/feldroy | PyPI https://pypi.org/user/audreyr/
* Free software: MIT License

## Features

`annotated-types` is for validation. AirField is for presentation. Pydantic reads both.

```python
from pydantic import BaseModel
from airfield import AirField, Label, Widget, Autofocus, PrimaryKey

class Article(BaseModel):
    id: int = AirField(primary_key=True)
    title: str = AirField(label="Title", autofocus=True)
    email: str = AirField(type="email", label="Email Address")
    body: str = AirField(widget="textarea", placeholder="Write something...")
```

> **Note:** AirField works with any Pydantic `BaseModel`. If you're using [Air](https://github.com/feldroy/air), use `AirModel` instead, which extends BaseModel with ORM and form support.

Every parameter produces a typed, frozen dataclass in `field_info.metadata`. Consumers discover metadata with `isinstance` checks:

```python
for m in field_info.metadata:
    if isinstance(m, Widget):
        render_input(m.kind)
    elif isinstance(m, Label):
        render_label(m.text)
    elif isinstance(m, PrimaryKey):
        make_read_only()
```

Two ways to declare, same result:

```python
# Convenience function
email: str = AirField(type="email", label="Email")

# Annotated metadata (composable with annotated-types, etc.)
email: Annotated[str, Widget("email"), Label("Email")]
```

### Presentation types

| Type | Purpose |
|---|---|
| `PrimaryKey` | Field is the record identity (affects visibility, editability, linking) |
| `Label` | Human-readable display name |
| `Placeholder` | Hint text when the field is empty |
| `HelpText` | Explanatory text that supplements the label |
| `Widget` | Preferred input mechanism (`"email"`, `"textarea"`, `"date"`, ...) |
| `DisplayFormat` | How to format the value for display (`"currency"`, `"percent"`, ...) |
| `Choices` | Constrain to labeled options (select, radio, combobox) |
| `Autofocus` | This field receives focus when the UI loads |
| `Hidden` | Field is not shown in specified contexts |
| `ReadOnly` | Field is displayed but not editable |
| `Filterable` | Field appears in search/filter UI |
| `Sortable` | Field is sortable in list/table views |
| `ColumnAlign` | Left/center/right alignment in tables |
| `ColumnWidth` | Relative width in table columns |
| `Grouped` | Assigns to a named group for layout |
| `Priority` | Importance relative to siblings |
| `Compact` | How to represent in space-constrained contexts |

## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://feldroy.github.io/AirField/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/AirField.git
cd AirField

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `airfield`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## Author

AirField was created in 2026 by Audrey M. Roy Greenfeld.

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
