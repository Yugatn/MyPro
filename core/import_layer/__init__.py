"""Universal import layer."""

from .base import ImportAdapter, ImportResult
from .otio_adapter import OTIOAdapter
from .reports import (
    ImportManifest, LossEntry, LossReport, MappingEntry, MappingReport,
    RelinkEntry, RelinkingReport, SourceDescriptor,
)
from .service import ImportProposal, ImportService

__all__ = [
    "ImportAdapter", "ImportResult", "OTIOAdapter",
    "ImportManifest", "LossEntry", "LossReport", "MappingEntry", "MappingReport",
    "RelinkEntry", "RelinkingReport", "SourceDescriptor",
    "ImportProposal", "ImportService",
]
