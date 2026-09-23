"""Backend interface."""
from __future__ import annotations
from abc import ABC, abstractmethod
from .result import RenderResult
from .specification import RenderSpecification

class RenderBackend(ABC):
    @abstractmethod
    def render(self, repository, specification: RenderSpecification, *, execute: bool = True) -> RenderResult:
        raise NotImplementedError
