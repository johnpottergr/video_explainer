"""Script generator - creates video scripts from content analysis."""

from ..config import Config, load_config
from ..models import (
    ContentAnalysis,
    ParsedDocument,
    Script,
    ScriptScene,
    VisualCue,
)
from ..understanding.llm_provider import LLMProvider, get_llm_provider


SCRIPT_SYSTEM_PROMPT = """You are an expert video script writer specializing in technical
educational content. Your scripts are engaging, clear, and visually driven. You write
for a technical audience but explain concepts in accessible ways.

Your scripts should:
1. Start with a compelling hook that creates curiosity
2. Build concepts progressively, never assuming too much
3. Use analogies and concrete examples
4. Include clear visual cues that can be animated
5. End with a memorable takeaway

Always respond with valid JSON matching the requested schema."""


SCRIPT_USER_PROMPT_TEMPLATE = """Create a video script for the following technical content.

Document Title: {title}
Target Duration: {duration} seconds
Target Audience: {audience}

Core Thesis:
{thesis}

Key Concepts to Cover:
{concepts}

Source Content (for reference):
{content}

Create an engaging script with these requirements:
1. Hook (first 15 seconds): Create curiosity with a surprising fact or question
2. Context: Explain why this matters
3. Main explanation: Cover the key concepts with clear visual descriptions
4. Conclusion: Summarize with a memorable takeaway

For each scene, include:
- scene_type: hook, context, explanation, insight, or conclusion
- voiceover: The exact narration text (conversational, not academic)
- visual_cue: Detailed description of what should appear on screen
- duration_seconds: How long the scene should last

Respond with JSON matching this schema:
{{
  "title": "string",
  "total_duration_seconds": number,
  "source_document": "string",
  "scenes": [
    {{
      "scene_id": number,
      "scene_type": "hook|context|explanation|insight|conclusion",
      "title": "string",
      "voiceover": "string",
      "visual_cue": {{
        "description": "string",
        "visual_type": "animation|diagram|code|equation|image",
        "elements": ["string"],
        "duration_seconds": number
      }},
      "duration_seconds": number,
      "notes": "string"
    }}
  ]
}}"""


class ScriptGenerator:
    """Generates video scripts from content analysis."""

    def __init__(self, config: Config | None = None, llm: LLMProvider | None = None):
        """Initialize the generator.

        Args:
            config: Configuration object. If None, loads default.
            llm: LLM provider. If None, creates one from config.
        """
        self.config = config or load_config()
        self.llm = llm or get_llm_provider(self.config)

    def generate(
        self,
        document: ParsedDocument,
        analysis: ContentAnalysis,
        target_duration: int | None = None,
    ) -> Script:
        """Generate a video script from analyzed content.

        Args:
            document: The parsed source document
            analysis: Content analysis with key concepts
            target_duration: Target duration in seconds (uses analysis suggestion if None)

        Returns:
            Script with scenes and visual cues
        """
        duration = target_duration or analysis.suggested_duration_seconds

        # Format concepts for the prompt
        concepts_text = "\n".join(
            f"- {c.name}: {c.explanation} (complexity: {c.complexity}/10, "
            f"visual potential: {c.visual_potential})"
            for c in analysis.key_concepts
        )

        # Get content from document
        content_parts = []
        for section in document.sections[:10]:  # Limit sections
            content_parts.append(f"## {section.heading}\n{section.content[:1000]}")
        content_text = "\n\n".join(content_parts)

        # Build the prompt
        prompt = SCRIPT_USER_PROMPT_TEMPLATE.format(
            title=document.title,
            duration=duration,
            audience=analysis.target_audience,
            thesis=analysis.core_thesis,
            concepts=concepts_text,
            content=content_text[:10000],  # Limit total content
        )

        # Generate script via LLM
        result = self.llm.generate_json(prompt, SCRIPT_SYSTEM_PROMPT)

        # Parse into Script model
        return self._parse_script_result(result, document.source_path)

    def _parse_script_result(self, result: dict, source_path: str) -> Script:
        """Parse LLM result into a Script model."""
        scenes = []
        for s in result.get("scenes", []):
            visual_cue_data = s.get("visual_cue", {})
            visual_cue = VisualCue(
                description=visual_cue_data.get("description", ""),
                visual_type=visual_cue_data.get("visual_type", "animation"),
                elements=visual_cue_data.get("elements", []),
                duration_seconds=visual_cue_data.get(
                    "duration_seconds", s.get("duration_seconds", 10.0)
                ),
            )

            scene = ScriptScene(
                scene_id=s.get("scene_id", len(scenes) + 1),
                scene_type=s.get("scene_type", "explanation"),
                title=s.get("title", ""),
                voiceover=s.get("voiceover", ""),
                visual_cue=visual_cue,
                duration_seconds=s.get("duration_seconds", 10.0),
                notes=s.get("notes", ""),
            )
            scenes.append(scene)

        total_duration = sum(s.duration_seconds for s in scenes)

        return Script(
            title=result.get("title", "Untitled"),
            total_duration_seconds=total_duration,
            scenes=scenes,
            source_document=source_path,
        )

    def format_script_for_review(self, script: Script) -> str:
        """Format a script for human review.

        Args:
            script: The script to format

        Returns:
            Formatted string representation suitable for review
        """
        lines = [
            f"# {script.title}",
            f"",
            f"**Total Duration**: {script.total_duration_seconds:.0f} seconds "
            f"({script.total_duration_seconds / 60:.1f} minutes)",
            f"**Source**: {script.source_document}",
            f"**Scenes**: {len(script.scenes)}",
            "",
            "---",
            "",
        ]

        for scene in script.scenes:
            timestamp = sum(
                s.duration_seconds
                for s in script.scenes
                if s.scene_id < scene.scene_id
            )
            minutes = int(timestamp // 60)
            seconds = int(timestamp % 60)

            lines.extend([
                f"## Scene {scene.scene_id}: {scene.title}",
                f"**Type**: {scene.scene_type} | **Duration**: {scene.duration_seconds:.0f}s | "
                f"**Timestamp**: {minutes:02d}:{seconds:02d}",
                "",
                "### Voiceover",
                f"> {scene.voiceover}",
                "",
                "### Visual",
                f"**Type**: {scene.visual_cue.visual_type}",
                f"**Description**: {scene.visual_cue.description}",
                "",
                f"**Elements**: {', '.join(scene.visual_cue.elements) if scene.visual_cue.elements else 'None specified'}",
                "",
            ])

            if scene.notes:
                lines.extend([
                    f"**Notes**: {scene.notes}",
                    "",
                ])

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def save_script(self, script: Script, path: str) -> None:
        """Save a script to a file.

        Args:
            script: The script to save
            path: Path to save the script
        """
        import json
        from pathlib import Path

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as JSON for machine processing
        with open(output_path, "w") as f:
            json.dump(script.model_dump(), f, indent=2)

        # Also save human-readable version
        readable_path = output_path.with_suffix(".md")
        with open(readable_path, "w") as f:
            f.write(self.format_script_for_review(script))

    @staticmethod
    def load_script(path: str) -> Script:
        """Load a script from a file.

        Args:
            path: Path to the script file

        Returns:
            Loaded Script object
        """
        import json
        from pathlib import Path

        with open(Path(path)) as f:
            data = json.load(f)

        return Script(**data)
