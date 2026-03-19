"""AirField: UI presentation vocabulary for Pydantic models.

annotated-types is for validation. airfield is for presentation.
Define once on the model, render anywhere.
"""

from airfield.main import AirField as AirField
from airfield.types import Autofocus as Autofocus
from airfield.types import BasePresentation as BasePresentation
from airfield.types import Choices as Choices
from airfield.types import ColumnAlign as ColumnAlign
from airfield.types import ColumnWidth as ColumnWidth
from airfield.types import Compact as Compact
from airfield.types import CsrfToken as CsrfToken
from airfield.types import DisplayFormat as DisplayFormat
from airfield.types import Filterable as Filterable
from airfield.types import Grouped as Grouped
from airfield.types import HelpText as HelpText
from airfield.types import Hidden as Hidden
from airfield.types import Label as Label
from airfield.types import Placeholder as Placeholder
from airfield.types import PrimaryKey as PrimaryKey
from airfield.types import Priority as Priority
from airfield.types import ReadOnly as ReadOnly
from airfield.types import Sortable as Sortable
from airfield.types import Widget as Widget

__all__ = [
    "AirField",
    "Autofocus",
    "BasePresentation",
    "Choices",
    "ColumnAlign",
    "ColumnWidth",
    "Compact",
    "CsrfToken",
    "DisplayFormat",
    "Filterable",
    "Grouped",
    "HelpText",
    "Hidden",
    "Label",
    "Placeholder",
    "PrimaryKey",
    "Priority",
    "ReadOnly",
    "Sortable",
    "Widget",
]
