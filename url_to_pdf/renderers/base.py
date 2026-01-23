from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol, runtime_checkable

from .document import Document


@dataclass
class RenderOptions:
    font_family: Optional[str] = None
    include_images: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Renderer(Protocol):
    @property
    def format_name(self) -> str: ...

    @property
    def file_extension(self) -> str: ...

    def render(
        self, document: Document, output_path: Path, options: Optional[RenderOptions] = None
    ) -> Path: ...


class BaseRenderer(ABC):
    SUPPORTED_FEATURES: set[str] = set()  # "fonts", "images", "links", "toc"

    @property
    @abstractmethod
    def format_name(self) -> str: ...

    @property
    @abstractmethod
    def file_extension(self) -> str: ...

    @abstractmethod
    def render(
        self, document: Document, output_path: Path, options: Optional[RenderOptions] = None
    ) -> Path: ...

    def supports_feature(self, feature: str) -> bool:
        return feature in self.SUPPORTED_FEATURES


class RenderError(Exception):
    pass
