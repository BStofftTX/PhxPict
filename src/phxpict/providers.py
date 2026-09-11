from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import re
from typing import Any, Callable, Iterable, Sequence


DEFAULT_CATEGORIES = {
    "people": {"people", "person", "portrait", "profile", "face", "family", "friend"},
    "nature": {"nature", "forest", "tree", "flower", "mountain", "river", "lake", "beach", "sunset"},
    "buildings": {"building", "house", "home", "office", "church", "tower", "architecture"},
    "automobiles": {"automobile", "car", "truck", "vehicle", "sedan", "suv"},
    "trains": {"train", "rail", "railroad", "locomotive"},
    "planes": {"plane", "airplane", "aircraft", "jet", "aviation"},
    "warfare": {"war", "warfare", "military", "army", "navy", "marine", "weapon", "tank", "soldier"},
}

# Labels are deliberately concrete because CLIP compares an image with text.
# The public/search tag remains the stable dictionary key.
VISUAL_CATEGORY_LABELS = {
    "people": "a person, face, portrait, or profile",
    "nature": "nature, landscape, plants, wildlife, mountains, water, or forest",
    "buildings": "a building, house, architecture, city, or structure",
    "automobiles": "a car, truck, automobile, or road vehicle",
    "trains": "a train, locomotive, railroad, or railway",
    "planes": "an airplane, aircraft, jet, or aviation scene",
    "warfare": "warfare, military personnel, weapons, tanks, or combat",
}


class ProviderUnavailableError(RuntimeError):
    """Raised when an optional content provider cannot run locally."""


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


class LocalCLIPTagProvider(ContentTagProvider):
    """Local zero-shot visual classifier backed by Hugging Face CLIP.

    The model is loaded once and inference happens in this Python process. The
    first use may download model weights, but photographs are never uploaded.
    ``classifier`` is injectable so provider integration can be tested without
    downloading a model.
    """

    name = "local-clip"

    def __init__(
        self,
        model: str = "openai/clip-vit-base-patch32",
        *,
        classifier: Callable[..., Sequence[dict[str, Any]]] | None = None,
        category_labels: dict[str, str] | None = None,
        minimum_score: float = 0.15,
        relative_score: float = 0.72,
        max_tags: int = 3,
    ):
        self.model = model
        self._classifier = classifier
        self.category_labels = category_labels or VISUAL_CATEGORY_LABELS
        self.minimum_score = minimum_score
        self.relative_score = relative_score
        self.max_tags = max_tags

    def _load_classifier(self) -> Callable[..., Sequence[dict[str, Any]]]:
        if self._classifier is not None:
            return self._classifier
        try:
            from transformers import pipeline

            self._classifier = pipeline(
                "zero-shot-image-classification",
                model=self.model,
                device=-1,
            )
        except (ImportError, ModuleNotFoundError) as exc:
            raise ProviderUnavailableError(
                "Local visual search requires the optional 'visual' dependencies"
            ) from exc
        except Exception as exc:
            raise ProviderUnavailableError(
                f"Could not load local visual model {self.model!r}: {exc}"
            ) from exc
        return self._classifier

    def tags_for(self, image_path: Path) -> list[str]:
        classifier = self._load_classifier()
        labels = list(self.category_labels.values())
        try:
            predictions = classifier(
                str(image_path),
                candidate_labels=labels,
                hypothesis_template="This is a photo of {}.",
            )
        except Exception as exc:
            raise ProviderUnavailableError(f"Local visual inference failed: {exc}") from exc

        by_label = {
            str(item.get("label")): float(item.get("score", 0.0))
            for item in predictions
        }
        ranked = sorted(
            ((category, by_label.get(label, 0.0)) for category, label in self.category_labels.items()),
            key=lambda item: item[1],
            reverse=True,
        )
        if not ranked or ranked[0][1] <= 0:
            return []
        cutoff = max(self.minimum_score, ranked[0][1] * self.relative_score)
        return sorted(category for category, score in ranked[: self.max_tags] if score >= cutoff)


class GracefulFallbackTagProvider(ContentTagProvider):
    """Use the visual provider when possible and retain deterministic tags."""

    name = "local-visual-with-fallback"

    def __init__(
        self,
        primary: ContentTagProvider,
        fallback: ContentTagProvider | None = None,
    ):
        self.primary = primary
        self.fallback = fallback or FilenameTagProvider()
        self.primary_enabled = True
        self.fallback_reason: str | None = None

    def tags_for(self, image_path: Path) -> list[str]:
        tags = set(self.fallback.tags_for(image_path))
        if self.primary_enabled:
            try:
                tags.update(self.primary.tags_for(image_path))
            except ProviderUnavailableError as exc:
                self.primary_enabled = False
                self.fallback_reason = str(exc)
        return sorted(tags)


def build_tag_provider(mode: str = "auto", model: str | None = None) -> ContentTagProvider:
    """Build the configured local provider without making network API calls."""

    if mode == "filename":
        return FilenameTagProvider()
    visual = LocalCLIPTagProvider(model=model or "openai/clip-vit-base-patch32")
    if mode == "clip":
        return visual
    if mode == "auto":
        return GracefulFallbackTagProvider(visual)
    raise ValueError("mode must be auto, filename, or clip")
