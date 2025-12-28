"""Animation rendering module with pluggable backends."""

from .renderer import (
    AnimationRenderer,
    MockRenderer,
    MotionCanvasRenderer,  # Backward compatibility alias
    RemotionRenderer,
    RenderResult,
    get_renderer,
)

__all__ = [
    "AnimationRenderer",
    "MockRenderer",
    "MotionCanvasRenderer",
    "RemotionRenderer",
    "RenderResult",
    "get_renderer",
]
