# AirField

Dataclasses that describe how Pydantic model fields should be presented in any UI context: web forms, CLI prompts, data tables, notebooks, API docs, charts.

`annotated-types` is for validation. AirField is for presentation. Pydantic reads both.

```python
from pydantic import BaseModel
from airfield import AirField

class Article(BaseModel):
    id: int = AirField(primary_key=True)
    title: str = AirField(label="Title", autofocus=True)
    email: str = AirField(type="email", label="Email Address")
    body: str = AirField(widget="textarea", placeholder="Write something...")
```

!!! note
    AirField works with any Pydantic `BaseModel`. If you're using [Air](https://github.com/feldroy/air), use `AirModel` instead, which extends BaseModel with ORM and form support.

## Getting started

- [Installation](installation.md) -- how to install AirField
- [Usage](usage.md) -- the convenience function, the Annotated path, reading metadata, all types
- [API Reference](api.md) -- auto-generated from docstrings
