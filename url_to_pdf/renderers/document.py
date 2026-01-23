from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Union


class InlineType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    LINK = "link"


@dataclass
class InlineElement:
    type: InlineType
    content: str
    url: Optional[str] = None


@dataclass
class HeadingBlock:
    level: int  # 1-6
    content: list[InlineElement]


@dataclass
class ParagraphBlock:
    content: list[InlineElement]


@dataclass
class ImageBlock:
    path: Optional[Path] = None  # Local path
    url: Optional[str] = None  # Image URL
    alt: str = ""
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class HorizontalRuleBlock:
    pass


ContentBlockType = Union[HeadingBlock, ParagraphBlock, ImageBlock, HorizontalRuleBlock]


@dataclass
class DocumentMetadata:
    title: str
    authors: list[str] = field(default_factory=list)
    source_url: Optional[str] = None
    language: Optional[str] = None


@dataclass
class Document:
    metadata: DocumentMetadata
    blocks: list[ContentBlockType] = field(default_factory=list)
