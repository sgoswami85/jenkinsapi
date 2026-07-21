"""Job data sources. Only compliant, ToS-friendly APIs/feeds live here."""

from .base import JobSource
from .adzuna import AdzunaSource
from .sample import SampleSource

__all__ = ["JobSource", "AdzunaSource", "SampleSource"]
