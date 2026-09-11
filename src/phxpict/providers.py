from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import re
from typing import Iterable


DEFAULT_CATEGORIES = {
    "people": {"people", "person", "portrait", "profile", "face", "family", "friend"},
    "nature": {"nature", "forest", "tree", "flower", "mountain", "river", "lake", "beach", "sunset"},
    "buildings": {"building", "house", "home", "office", "church", "tower", "architecture"},
    "automobiles": {"automobile", "car", "truck", "vehicle", "sedan", "suv"},
    "trains": {"train", "rail", "railroad", "locomotive"},
    "planes": {"plane", "airplane", "aircraft", "jet", "aviation"},
    "warfare": {"war", "warfare", "military", "army", "navy", "marine", "weapon", "tank", "soldier"},
}


class ContentTagProvider(ABC):
    """Extension point for deterministic or ML-backed visual tagging."""

    name = "abstract"

    @abstractmethod
    def tags_for(self, image_path: Path) -> list[str]:
        raise NotImplementedError


class FilenameTagProvider(ContentTagProvider):
    """Offline baseline using filename and folder words; deterministic and testable."""

    name = "filename-baseline"

    def __init__(self, categories: dict[str, Iterable[str]] | None = None):
        self.categories = categories or DEFAULT_CATEGORIES

    def tags_for(self, image_path: Path) -> list[str]:
        words = set(re.findall(r"[a-z0-9]+", str(image_path).lower()))
        tags = {
            category
            for category, synonyms in self.categories.items()
            if words.intersection(set(synonyms))
        }
        return sorted(tags)


class CompositeTagProvider(ContentTagProvider):
    name = "composite"

    def __init__(self, providers: Iterable[ContentTagProvider]):
        self.providers = list(providers)

    def tags_for(self, image_path: Path) -> list[str]:
        tags: set[str] = set()
        for provider in self.providers:
            tags.update(provider.tags_for(image_path))
        return sorted(tags)

