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
    """Mock LLM provider that returns pre-computed responses for testing.

    This provider recognizes certain patterns in prompts and returns
    realistic responses for the LLM inference article content.
    """

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a mock response based on prompt patterns."""
        # For now, return a generic response
        # Specific responses are handled in generate_json for structured outputs
        return "This is a mock LLM response for testing purposes."

    def generate_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict[str, Any]:
        """Generate mock JSON responses for known prompt patterns."""
        prompt_lower = prompt.lower()

        # Content analysis request
        if "analyze" in prompt_lower and ("content" in prompt_lower or "document" in prompt_lower):
            return self._mock_content_analysis()

        # Script generation request
        if "script" in prompt_lower and ("generate" in prompt_lower or "create" in prompt_lower):
            return self._mock_script_generation()

        # Storyboard generation request
        if "storyboard" in prompt_lower:
            return self._mock_storyboard_generation()

        # Default empty response
        return {}

    def _mock_content_analysis(self) -> dict[str, Any]:
        """Return mock content analysis for LLM inference article."""
        return {
            "core_thesis": "LLM inference can be optimized from 40 to 3,500+ tokens/second through KV caching, continuous batching, and PagedAttention, because the decode phase is memory-bandwidth bound rather than compute bound.",
            "key_concepts": [
                {
                    "name": "Prefill Phase",
                    "explanation": "The initial phase where all input tokens are processed in parallel. This phase is compute-bound, fully utilizing GPU tensor cores for matrix multiplications.",
                    "complexity": 6,
                    "prerequisites": ["transformer architecture", "matrix multiplication"],
                    "analogies": ["Like reading an entire book before answering questions about it"],
                    "visual_potential": "high"
                },
                {
                    "name": "Decode Phase",
                    "explanation": "The autoregressive phase where output tokens are generated one at a time. Each token requires loading all model weights from memory, making it memory-bandwidth bound.",
                    "complexity": 7,
                    "prerequisites": ["prefill phase", "GPU memory architecture"],
                    "analogies": ["Like typing one letter at a time, waiting for each to appear before typing the next"],
                    "visual_potential": "high"
                },
                {
                    "name": "Attention Mechanism",
                    "explanation": "The operation that allows each token to 'look at' every other token using Query, Key, and Value vectors. Computes relevance scores via softmax(QK^T/√d)V.",
                    "complexity": 8,
                    "prerequisites": ["linear algebra", "softmax function"],
                    "analogies": ["Like a spotlight that can focus on multiple parts of a sentence at once to understand context"],
                    "visual_potential": "high"
                },
                {
                    "name": "KV Cache",
                    "explanation": "An optimization that stores computed Key and Value vectors for previous tokens, avoiding redundant recomputation during decode. Transforms O(n²) work to O(n).",
                    "complexity": 6,
                    "prerequisites": ["attention mechanism", "decode phase"],
                    "analogies": ["Like keeping notes instead of re-reading the entire book for each new question"],
                    "visual_potential": "high"
                },
                {
                    "name": "Memory Bandwidth Bottleneck",
                    "explanation": "The fundamental limitation in decode: we must load 14GB of weights for each token, but can only transfer 2TB/s on an A100, limiting us to ~140 tokens/second per sequence.",
                    "complexity": 7,
                    "prerequisites": ["GPU architecture", "arithmetic intensity"],
                    "analogies": ["Like a highway that can only carry so many cars, no matter how fast the cars can go"],
                    "visual_potential": "medium"
                }
            ],
            "target_audience": "Technical professionals interested in ML infrastructure, GPU programming, or AI systems",
            "suggested_duration_seconds": 240,
            "complexity_score": 7
        }

    def _mock_script_generation(self) -> dict[str, Any]:
        """Return mock script for the Prefill/Decode/KV Cache explanation."""
        return {
            "title": "How LLM Inference Actually Works: From 40 to 3,500 Tokens Per Second",
            "total_duration_seconds": 210,
            "source_document": "post.md",
            "scenes": [
                {
                    "scene_id": 1,
                    "scene_type": "hook",
                    "title": "The Speed Problem",
                    "voiceover": "Every time you send a message to ChatGPT, something remarkable happens. A neural network with billions of parameters generates a response, one token at a time. The naive approach? Forty tokens per second. What the best systems achieve? Over three thousand five hundred. This is how they do it.",
                    "visual_cue": {
                        "description": "Show a chat interface with tokens appearing slowly, then speed up dramatically",
                        "visual_type": "animation",
                        "elements": ["chat_bubble", "token_counter", "speed_indicator"],
                        "duration_seconds": 15.0
                    },
                    "duration_seconds": 15.0,
                    "notes": "Build intrigue with the 87x improvement"
                },
                {
                    "scene_id": 2,
                    "scene_type": "context",
                    "title": "The Two Phases",
                    "voiceover": "LLM inference has two distinct phases, and understanding them is the key to everything. The first is called prefill. When you send a prompt, the model processes all your input tokens in parallel, in one forward pass. This phase is compute-bound. The GPU's tensor cores are working at full capacity.",
                    "visual_cue": {
                        "description": "Split screen showing prefill: multiple tokens lighting up simultaneously, GPU utilization at 100%",
                        "visual_type": "animation",
                        "elements": ["token_grid", "gpu_utilization_bar", "parallel_arrows"],
                        "duration_seconds": 20.0
                    },
                    "duration_seconds": 20.0,
                    "notes": "Establish the parallel nature of prefill"
                },
                {
                    "scene_id": 3,
                    "scene_type": "explanation",
                    "title": "The Decode Bottleneck",
                    "voiceover": "Then comes decode, and everything changes. Now we generate tokens one at a time. For each single token, we must load the entire model, all fourteen gigabytes of weights, from GPU memory. On an A100 with two terabytes per second bandwidth, that's seven milliseconds minimum per token. The GPU sits mostly idle, waiting for data. We're not limited by compute. We're limited by memory bandwidth.",
                    "visual_cue": {
                        "description": "Show decode: single token lighting up, weights streaming from memory, GPU utilization dropping to ~5%, memory bandwidth bar full",
                        "visual_type": "animation",
                        "elements": ["single_token", "weight_stream", "gpu_bar_low", "memory_bar_high", "roofline_diagram"],
                        "duration_seconds": 30.0
                    },
                    "duration_seconds": 30.0,
                    "notes": "Key insight: memory-bound, not compute-bound"
                },
                {
                    "scene_id": 4,
                    "scene_type": "explanation",
                    "title": "Understanding Attention",
                    "voiceover": "To understand the solution, we need to understand attention. For each token, we compute three vectors: Query, Key, and Value. The Query asks 'what am I looking for?' The Key says 'what do I contain?' And the Value provides the actual information. Attention computes how much each token should focus on every other token, then aggregates the values accordingly.",
                    "visual_cue": {
                        "description": "Animated attention: show tokens, Q/K/V vectors emerging, attention matrix forming with softmax, values being weighted",
                        "visual_type": "animation",
                        "elements": ["tokens", "qkv_vectors", "attention_matrix", "softmax_highlight", "weighted_sum"],
                        "duration_seconds": 25.0
                    },
                    "duration_seconds": 25.0,
                    "notes": "Build up the attention mechanism visually"
                },
                {
                    "scene_id": 5,
                    "scene_type": "explanation",
                    "title": "The Redundancy Problem",
                    "voiceover": "Here's the problem with naive decode. To generate token one hundred, we need to compute attention over all previous tokens. That means computing Keys and Values for tokens one through ninety-nine, even though they haven't changed since we computed them before. The work grows quadratically. For a thousand-token response, we're doing five hundred thousand times more work than necessary.",
                    "visual_cue": {
                        "description": "Show growing computation: token counter climbing, work multiplying, O(n²) visualized as expanding grid",
                        "visual_type": "animation",
                        "elements": ["token_counter", "work_counter", "quadratic_grid", "waste_highlight"],
                        "duration_seconds": 25.0
                    },
                    "duration_seconds": 25.0,
                    "notes": "Make the waste viscerally clear"
                },
                {
                    "scene_id": 6,
                    "scene_type": "insight",
                    "title": "The KV Cache Solution",
                    "voiceover": "The solution is elegant: compute each Key and Value exactly once, then cache them. When we generate token one hundred, we only compute K and V for that new token, then look up the cached values for tokens one through ninety-nine. This transforms quadratic work into linear. We're no longer recomputing. We're just remembering.",
                    "visual_cue": {
                        "description": "Show KV cache growing: new K/V added to cache stack, lookup arrows to previous values, O(n²)→O(n) transformation",
                        "visual_type": "animation",
                        "elements": ["kv_cache_stack", "new_kv_entry", "lookup_arrows", "complexity_counter"],
                        "duration_seconds": 25.0
                    },
                    "duration_seconds": 25.0,
                    "notes": "The aha moment - caching eliminates redundancy"
                },
                {
                    "scene_id": 7,
                    "scene_type": "explanation",
                    "title": "How KV Cache Works",
                    "voiceover": "During decode, the new token's Query vector attends to all the cached Keys. We compute Q times K-transpose, apply softmax to get attention weights, then multiply by the cached Values. The cache lookup is essentially free, it's just a matrix multiply against tensors already in memory. No recomputation needed.",
                    "visual_cue": {
                        "description": "Technical diagram: Q vector querying K cache, attention weights visualized, V cache multiplication",
                        "visual_type": "animation",
                        "elements": ["q_vector", "k_cache", "attention_weights", "v_cache", "output_vector"],
                        "duration_seconds": 20.0
                    },
                    "duration_seconds": 20.0,
                    "notes": "Show the mechanics clearly"
                },
                {
                    "scene_id": 8,
                    "scene_type": "conclusion",
                    "title": "The Impact",
                    "voiceover": "This single optimization is always enabled in production systems. It's so fundamental that there's no off switch. Combined with other techniques like continuous batching and PagedAttention, we go from forty tokens per second to over thirty-five hundred. An eighty-seven times improvement. And it all starts with one insight: don't recompute what you can remember.",
                    "visual_cue": {
                        "description": "Before/after comparison: throughput bars rising from 40 to 3500, then fade to key insight text",
                        "visual_type": "animation",
                        "elements": ["throughput_comparison", "optimization_stack", "key_insight_text"],
                        "duration_seconds": 25.0
                    },
                    "duration_seconds": 25.0,
                    "notes": "End with the concrete improvement and memorable takeaway"
                }
            ]
        }

    def _mock_storyboard_generation(self) -> dict[str, Any]:
        """Return mock storyboard (abbreviated for now)."""
        return {
            "title": "LLM Inference Explainer",
            "scenes": [],
            "style_guide": {
                "background": "#0f0f1a",
                "primary": "#00d9ff",
                "secondary": "#ff6b35",
                "success": "#00ff88"
            },
            "total_duration_seconds": 210
        }


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider (placeholder)."""

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        raise NotImplementedError("Anthropic provider not yet implemented")

    def generate_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict[str, Any]:
        raise NotImplementedError("Anthropic provider not yet implemented")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (placeholder)."""

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        raise NotImplementedError("OpenAI provider not yet implemented")

    def generate_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict[str, Any]:
        raise NotImplementedError("OpenAI provider not yet implemented")


def get_llm_provider(config: Config | None = None) -> LLMProvider:
    """Get the appropriate LLM provider based on configuration.

    Args:
        config: Configuration object. If None, uses default config.

    Returns:
        An LLM provider instance
    """
    if config is None:
        from ..config import load_config
        config = load_config()

    provider_name = config.llm.provider.lower()

    if provider_name == "mock":
        return MockLLMProvider(config.llm)
    elif provider_name == "anthropic":
        return AnthropicProvider(config.llm)
    elif provider_name == "openai":
        return OpenAIProvider(config.llm)
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
