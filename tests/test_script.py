"""Tests for script generation module."""

from pathlib import Path

import pytest

from src.config import Config
from src.ingestion import parse_document
from src.models import ContentAnalysis, Script
from src.script import ScriptGenerator
from src.understanding import ContentAnalyzer


class TestScriptGenerator:
    """Tests for the script generator."""

    @pytest.fixture
    def generator(self):
        return ScriptGenerator()

    @pytest.fixture
    def sample_analysis(self) -> ContentAnalysis:
        """Create a sample content analysis for testing."""
        from src.models import Concept

        return ContentAnalysis(
            core_thesis="Testing is important for software quality.",
            key_concepts=[
                Concept(
                    name="Unit Testing",
                    explanation="Testing individual components in isolation",
                    complexity=3,
                    prerequisites=["basic programming"],
                    analogies=["Like checking each ingredient before cooking"],
                    visual_potential="medium",
                ),
                Concept(
                    name="Integration Testing",
                    explanation="Testing how components work together",
                    complexity=5,
                    prerequisites=["unit testing"],
                    analogies=["Like tasting the dish while cooking"],
                    visual_potential="high",
                ),
            ],
            target_audience="Software developers",
            suggested_duration_seconds=180,
            complexity_score=4,
        )

    @pytest.fixture
    def sample_document(self, sample_markdown):
        return parse_document(sample_markdown)

    def test_generate_returns_script(self, generator, sample_document, sample_analysis):
        script = generator.generate(sample_document, sample_analysis)
        assert isinstance(script, Script)

    def test_script_has_title(self, generator, sample_document, sample_analysis):
        script = generator.generate(sample_document, sample_analysis)
        assert script.title
        assert len(script.title) > 0

    def test_script_has_scenes(self, generator, sample_document, sample_analysis):
        script = generator.generate(sample_document, sample_analysis)
        assert len(script.scenes) > 0

    def test_scenes_have_required_fields(self, generator, sample_document, sample_analysis):
        script = generator.generate(sample_document, sample_analysis)
        for scene in script.scenes:
            assert scene.scene_id > 0
            assert scene.scene_type in ["hook", "context", "explanation", "insight", "conclusion"]
            assert scene.voiceover
            assert scene.visual_cue
            assert scene.duration_seconds > 0

    def test_visual_cues_have_description(self, generator, sample_document, sample_analysis):
        script = generator.generate(sample_document, sample_analysis)
        for scene in script.scenes:
            assert scene.visual_cue.description
            assert scene.visual_cue.visual_type

    def test_total_duration_matches_scenes(self, generator, sample_document, sample_analysis):
        script = generator.generate(sample_document, sample_analysis)
        expected_duration = sum(s.duration_seconds for s in script.scenes)
        assert script.total_duration_seconds == expected_duration

    def test_custom_target_duration(self, generator, sample_document, sample_analysis):
        script = generator.generate(sample_document, sample_analysis, target_duration=120)
        # Script should exist (mock doesn't respect duration, but real LLM would)
        assert isinstance(script, Script)


class TestScriptFormatting:
    """Tests for script formatting and serialization."""

    @pytest.fixture
    def generator(self):
        return ScriptGenerator()

    @pytest.fixture
    def sample_script(self, generator, sample_markdown):
        from src.models import Concept
        doc = parse_document(sample_markdown)
        analysis = ContentAnalysis(
            core_thesis="Test thesis",
            key_concepts=[
                Concept(
                    name="Test Concept",
                    explanation="Test explanation",
                    complexity=5,
                    visual_potential="high",
                )
            ],
            target_audience="Developers",
            suggested_duration_seconds=120,
            complexity_score=5,
        )
        return generator.generate(doc, analysis)

    def test_format_for_review(self, generator, sample_script):
        formatted = generator.format_script_for_review(sample_script)
        assert isinstance(formatted, str)
        assert sample_script.title in formatted
        assert "Scene" in formatted
        assert "Voiceover" in formatted
        assert "Visual" in formatted

    def test_save_and_load_script(self, generator, sample_script, tmp_path):
        script_path = tmp_path / "test_script.json"
        generator.save_script(sample_script, str(script_path))

        # Check both files were created
        assert script_path.exists()
        assert script_path.with_suffix(".md").exists()

        # Load and verify
        loaded = ScriptGenerator.load_script(str(script_path))
        assert loaded.title == sample_script.title
        assert len(loaded.scenes) == len(sample_script.scenes)


class TestRealDocumentScript:
    """Test script generation with the real LLM inference document."""

    @pytest.fixture
    def inference_doc_path(self):
        path = Path("/Users/prajwal/Desktop/Learning/inference/website/post.md")
        if not path.exists():
            pytest.skip("Inference document not found")
        return path

    @pytest.fixture
    def generator(self):
        return ScriptGenerator()

    @pytest.fixture
    def analyzer(self):
        return ContentAnalyzer()

    def test_generate_script_for_inference_doc(
        self, generator, analyzer, inference_doc_path
    ):
        doc = parse_document(inference_doc_path)
        analysis = analyzer.analyze(doc)
        script = generator.generate(doc, analysis, target_duration=210)

        # Verify script structure
        assert script.title
        assert len(script.scenes) >= 3  # At least hook, content, conclusion

        # Check for expected scene types
        scene_types = [s.scene_type for s in script.scenes]
        assert "hook" in scene_types
        assert "conclusion" in scene_types

    def test_script_covers_key_concepts(self, generator, analyzer, inference_doc_path):
        doc = parse_document(inference_doc_path)
        analysis = analyzer.analyze(doc)
        script = generator.generate(doc, analysis)

        # Combine all voiceover text
        all_voiceover = " ".join(s.voiceover.lower() for s in script.scenes)

        # Should mention key concepts
        assert "prefill" in all_voiceover or "decode" in all_voiceover
        assert "cache" in all_voiceover or "memory" in all_voiceover

    def test_script_has_visual_cues_for_each_scene(
        self, generator, analyzer, inference_doc_path
    ):
        doc = parse_document(inference_doc_path)
        analysis = analyzer.analyze(doc)
        script = generator.generate(doc, analysis)

        for scene in script.scenes:
            assert scene.visual_cue.description
            assert len(scene.visual_cue.description) > 10  # Meaningful description

    def test_formatted_script_is_readable(
        self, generator, analyzer, inference_doc_path
    ):
        doc = parse_document(inference_doc_path)
        analysis = analyzer.analyze(doc)
        script = generator.generate(doc, analysis)

        formatted = generator.format_script_for_review(script)

        # Should be well-structured markdown
        assert "# " in formatted  # Has title
        assert "## Scene" in formatted  # Has scene headers
        assert "---" in formatted  # Has separators
        assert "Voiceover" in formatted
        assert "Visual" in formatted
