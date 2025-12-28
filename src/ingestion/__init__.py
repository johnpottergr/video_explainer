"""Content ingestion module - parse various document formats."""

from .markdown import parse_markdown
from .parser import parse_document

__all__ = ["parse_document", "parse_markdown"]
