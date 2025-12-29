"""LLM Provider abstraction and implementations."""

import json
from abc import ABC, abstractmethod
from typing import Any

from ..config import Config, LLMConfig
from ..models import ContentAnalysis, Concept, Script, ScriptScene, VisualCue


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt

        Returns:
            The generated text response
        """
        pass

    @abstractmethod
    def generate_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict[str, Any]:
        """Generate a JSON response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON response as a dictionary
        """
        pass


class MockLLMProvider(LLMProvider):
    """Mock LLM provider that returns generic responses for testing.

    This provider returns realistic but generic mock responses suitable
    for testing the pipeline without requiring an actual LLM API.
    """

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a mock response based on prompt patterns."""
        return "This is a mock LLM response for testing purposes."

    def generate_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict[str, Any]:
        """Generate mock JSON responses for known prompt patterns."""
        prompt_lower = prompt.lower()

        # Content analysis request
        if "analyze" in prompt_lower and (
            "content" in prompt_lower or "document" in prompt_lower
        ):
            return self._mock_content_analysis(prompt)

        # Storyboard generation request
        if "storyboard" in prompt_lower or "scene id:" in prompt_lower:
            return self._mock_storyboard_generation(prompt)

        # Script generation request
        if "script" in prompt_lower and (
            "generate" in prompt_lower or "create" in prompt_lower
        ):
            return self._mock_script_generation(prompt)

        # Default empty response
        return {}

    def _mock_content_analysis(self, prompt: str) -> dict[str, Any]:
        """Return mock content analysis based on document content."""
        return {
            "core_thesis": "This document explains a technical concept with practical applications.",
            "key_concepts": [
                {
                    "name": "Core Concept",
                    "explanation": "The fundamental idea that drives the topic.",
                    "complexity": 5,
                    "prerequisites": ["basic understanding"],
                    "analogies": ["Like a simple real-world example"],
                    "visual_potential": "high",
                },
                {
                    "name": "Supporting Concept",
                    "explanation": "A related idea that helps understand the core concept.",
                    "complexity": 4,
                    "prerequisites": ["core concept"],
                    "analogies": ["Similar to another familiar concept"],
                    "visual_potential": "medium",
                },
                {
                    "name": "Application",
                    "explanation": "How this concept is used in practice.",
                    "complexity": 6,
                    "prerequisites": ["core concept", "supporting concept"],
                    "analogies": ["Like using a tool for a job"],
                    "visual_potential": "high",
                },
            ],
            "target_audience": "Technical professionals and enthusiasts",
            "estimated_duration_minutes": 3,
            "complexity_score": 5,
        }

    def _mock_script_generation(self, prompt: str) -> dict[str, Any]:
        """Return mock script for testing."""
        return {
            "title": "Understanding the Core Concept",
            "total_duration_seconds": 180,
            "source_document": "document.md",
            "scenes": [
                {
                    "scene_id": 1,
                    "scene_type": "hook",
                    "title": "The Problem",
                    "voiceover": "Every day, we encounter this challenge. What if there was a better way?",
                    "visual_cue": {
                        "description": "Show the problem visually",
                        "visual_type": "animation",
                        "elements": ["problem_illustration"],
                        "duration_seconds": 15.0,
                    },
                    "duration_seconds": 15.0,
                    "notes": "Build intrigue",
                },
                {
                    "scene_id": 2,
                    "scene_type": "context",
                    "title": "Background",
                    "voiceover": "To understand the solution, we first need to understand the context.",
                    "visual_cue": {
                        "description": "Show background context",
                        "visual_type": "animation",
                        "elements": ["context_diagram"],
                        "duration_seconds": 20.0,
                    },
                    "duration_seconds": 20.0,
                    "notes": "Set the stage",
                },
                {
                    "scene_id": 3,
                    "scene_type": "explanation",
                    "title": "The Core Concept",
                    "voiceover": "Here's how it works. The key insight is understanding the relationship between components.",
                    "visual_cue": {
                        "description": "Explain the core concept with visuals",
                        "visual_type": "animation",
                        "elements": ["concept_visualization"],
                        "duration_seconds": 30.0,
                    },
                    "duration_seconds": 30.0,
                    "notes": "Main explanation",
                },
                {
                    "scene_id": 4,
                    "scene_type": "insight",
                    "title": "The Key Insight",
                    "voiceover": "This is the breakthrough. Once you understand this, everything else falls into place.",
                    "visual_cue": {
                        "description": "Highlight the key insight",
                        "visual_type": "animation",
                        "elements": ["insight_highlight"],
                        "duration_seconds": 25.0,
                    },
                    "duration_seconds": 25.0,
                    "notes": "Aha moment",
                },
                {
                    "scene_id": 5,
                    "scene_type": "conclusion",
                    "title": "Putting It Together",
                    "voiceover": "Now you understand the concept. Let's see how it applies in practice.",
                    "visual_cue": {
                        "description": "Summary and application",
                        "visual_type": "animation",
                        "elements": ["summary"],
                        "duration_seconds": 20.0,
                    },
                    "duration_seconds": 20.0,
                    "notes": "Wrap up",
                },
            ],
        }

    def _mock_storyboard_generation(self, prompt: str = "") -> dict[str, Any]:
        """Return mock storyboard beats for testing."""
        return {
            "id": "test_storyboard",
            "title": "Test Storyboard",
            "duration_seconds": 60,
            "beats": [
                {
                    "id": "setup",
                    "start_seconds": 0,
                    "end_seconds": 10,
                    "voiceover": "Introduction to the concept.",
                    "elements": [
                        {
                            "id": "title",
                            "component": "title_card",
                            "props": {"heading": "Test Video", "subheading": "A demonstration"},
                            "position": {"x": "center", "y": "center"},
                            "enter": {"type": "fade", "duration_seconds": 0.5},
                            "exit": {"type": "fade", "duration_seconds": 0.5},
                        }
                    ],
                },
                {
                    "id": "main",
                    "start_seconds": 10,
                    "end_seconds": 50,
                    "voiceover": "The main explanation of the concept.",
                    "elements": [
                        {
                            "id": "content",
                            "component": "text_reveal",
                            "props": {"text": "Main content here"},
                            "position": {"x": "center", "y": "center"},
                        }
                    ],
                },
                {
                    "id": "conclusion",
                    "start_seconds": 50,
                    "end_seconds": 60,
                    "voiceover": "Summary and takeaways.",
                    "elements": [
                        {
                            "id": "outro",
                            "component": "title_card",
                            "props": {"heading": "Thank You"},
                            "position": {"x": "center", "y": "center"},
                        }
                    ],
                },
            ],
            "style": {
                "background_color": "#0f0f1a",
                "primary_color": "#00d9ff",
                "secondary_color": "#ff6b35",
                "font_family": "Inter",
            },
        }


def get_llm_provider(config: Config | None = None) -> LLMProvider:
    """Get the appropriate LLM provider based on configuration.

    Args:
        config: Configuration object. If None, loads default config.

    Returns:
        An LLM provider instance.

    Raises:
        ValueError: If provider name is not recognized.
    """
    if config is None:
        from ..config import load_config

        config = load_config()

    provider_name = config.llm.provider.lower()

    if provider_name == "mock":
        return MockLLMProvider(config.llm)
    elif provider_name == "anthropic":
        # TODO: Implement AnthropicLLMProvider
        raise NotImplementedError("Anthropic provider not yet implemented")
    elif provider_name == "openai":
        # TODO: Implement OpenAILLMProvider
        raise NotImplementedError("OpenAI provider not yet implemented")
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
