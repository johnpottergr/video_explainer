# Video Explainer System

A powerful system for generating high-quality explainer videos from technical documents. Transform research papers, articles, and documentation into engaging video content with automated narration and **programmatic animations**.

## Features

- **Document Parsing**: Parse Markdown documents with code blocks, equations, and images
- **Content Analysis**: Automatically extract key concepts and structure content for video
- **Script Generation**: Generate video scripts with visual cues and voiceover text
- **Text-to-Speech**: Integration with ElevenLabs TTS (with mock mode for development)
- **Remotion Animations**: React-based programmatic video generation - no manual animation required
- **Video Composition**: FFmpeg-based video assembly with audio overlay
- **Human-in-the-Loop**: CLI review interface for script approval and editing

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 20+
- FFmpeg

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd video_explainer

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -e .

# Install Node.js dependencies for Remotion animations
cd remotion
npm install
cd ..
```

### Generate Your First Video

```bash
# Generate with mock data (no API costs)
python generate_video.py --test

# Generate from a specific document
python generate_video.py --source path/to/document.md

# Generate from an existing script
python generate_video.py --script output/scripts/my_script.json
```

## Project Structure

```
video_explainer/
├── src/
│   ├── ingestion/          # Document parsing (Markdown, PDF, URL)
│   │   ├── markdown.py     # Markdown parser with section extraction
│   │   └── parser.py       # Main parser interface
│   ├── understanding/      # Content analysis
│   │   ├── llm_provider.py # LLM integration (Mock + real providers)
│   │   └── analyzer.py     # Content analyzer
│   ├── script/             # Script generation
│   │   └── generator.py    # Generate scripts with visual cues
│   ├── review/             # Human review interface
│   │   └── cli.py          # Rich-based CLI for script review
│   ├── audio/              # Text-to-Speech
│   │   └── tts.py          # ElevenLabs + Mock TTS providers
│   ├── animation/          # Animation rendering
│   │   └── renderer.py     # Abstract renderer + Remotion implementation
│   ├── composition/        # Video assembly
│   │   └── composer.py     # FFmpeg-based video composer
│   ├── pipeline/           # End-to-end orchestration
│   │   └── orchestrator.py # Video generation pipeline
│   ├── config.py           # Configuration management
│   └── models.py           # Pydantic data models
├── remotion/               # Remotion project (React-based animations)
│   ├── src/
│   │   ├── components/     # Reusable animation components
│   │   │   ├── TitleCard.tsx
│   │   │   ├── TokenGrid.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   └── TextReveal.tsx
│   │   ├── scenes/         # Scene compositions
│   │   │   ├── ExplainerVideo.tsx
│   │   │   └── SceneRenderer.tsx
│   │   └── types/          # TypeScript types
│   └── scripts/
│       └── render.mjs      # Headless rendering script
├── animations/             # Legacy Motion Canvas project (deprecated)
├── tests/                  # Test suite (119+ tests)
├── output/                 # Generated assets
├── Dockerfile              # Container setup
├── config.yaml             # Configuration file
└── generate_video.py       # CLI entry point
```

## Pipeline Architecture

```
Source Document → Parse → Analyze → Generate Script → TTS → Remotion → Compose → Video
       │            │         │            │           │        │          │
   Markdown      Sections   Concepts    Scenes      Audio    React      Final
     PDF         Headings   Insights    Visual      Files   Components   MP4
     URL         Code       Thesis      Cues                 Render
```

### Animation Generation

The system uses **Remotion** for programmatic video generation:

1. **Script visual cues** describe what should be shown (e.g., "token grid animation")
2. **SceneRenderer** maps visual cues to React components
3. **Remotion** renders the composition headlessly to video
4. **Composer** combines animation with TTS audio

Available animation components:
- `TitleCard` - Dramatic title reveals
- `TokenGrid` - Grid of tokens (prefill/decode visualization)
- `ProgressBar` - Animated utilization bars
- `TextReveal` - Text with fade-in animation

## Usage Examples

### Generate Video from Document

```python
from src.pipeline import VideoPipeline
from src.config import Config

# Load configuration
config = Config()

# Create pipeline (uses Remotion by default)
pipeline = VideoPipeline(config=config, output_dir="output")

# Set up progress callback
def on_progress(stage, percent):
    print(f"[{stage}] {percent:.0f}%")

pipeline.set_progress_callback(on_progress)

# Generate video
result = pipeline.generate_from_document(
    "path/to/document.md",
    target_duration=180,  # 3 minutes
)

if result.success:
    print(f"Video created: {result.output_path}")
    print(f"Duration: {result.duration_seconds}s")
    print(f"Renderer: {result.metadata['animation_renderer']}")
```

### Parse and Analyze Content

```python
from src.ingestion import parse_document
from src.understanding import ContentAnalyzer
from src.config import Config

# Parse document
document = parse_document("article.md")
print(f"Title: {document.title}")
print(f"Sections: {len(document.sections)}")

# Analyze content
config = Config()
analyzer = ContentAnalyzer(config)
analysis = analyzer.analyze(document)

print(f"Core thesis: {analysis.core_thesis}")
for concept in analysis.key_concepts:
    print(f"- {concept.name}: {concept.explanation}")
```

### Generate Script with Visual Cues

```python
from src.script import ScriptGenerator

script_gen = ScriptGenerator()
script = script_gen.generate(document, analysis, target_duration=180)

# Review script
print(script_gen.format_script_for_review(script))

# Save script
script_gen.save_script(script, "output/scripts/my_video.json")
```

## Configuration

Configuration is managed through `config.yaml`:

```yaml
llm:
  provider: mock  # mock | anthropic | openai
  model: claude-sonnet-4-20250514
  temperature: 0.7

tts:
  provider: mock  # mock | elevenlabs
  voice_id: null  # Uses default voice if not specified
  model: eleven_multilingual_v2

video:
  width: 1920
  height: 1080
  fps: 30
  format: mp4
```

Environment variables for API keys:
- `ANTHROPIC_API_KEY` - For Claude LLM provider
- `OPENAI_API_KEY` - For OpenAI LLM provider
- `ELEVENLABS_API_KEY` - For ElevenLabs TTS

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pipeline.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Quick unit tests (faster)
pytest tests/ --ignore=tests/test_e2e.py --ignore=tests/test_pipeline.py -v
```

## Docker

Build and run with Docker:

```bash
# Build image
docker build -t video-explainer .

# Run container
docker run -v $(pwd)/output:/app/output video-explainer

# With API keys
docker run -e ELEVENLABS_API_KEY=your_key \
           -v $(pwd)/output:/app/output \
           video-explainer
```

## Development

### Remotion Animations

Start the Remotion studio for development:

```bash
cd remotion
npm run dev
```

This opens a web-based editor at `http://localhost:3000` where you can preview compositions.

### Creating New Animation Components

Add new components in `remotion/src/components/`:

```tsx
import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

interface MyComponentProps {
  title: string;
  color: string;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, fps], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div style={{ opacity, color, fontSize: 48 }}>
      {title}
    </div>
  );
};
```

Then add it to `SceneRenderer.tsx` to map from visual cues.

### Programmatic Rendering

Render videos headlessly:

```bash
cd remotion
node scripts/render.mjs --props props.json --output video.mp4
```

## Visual Style

The default theme for technical content:

| Element | Color | Hex |
|---------|-------|-----|
| Background | Dark Slate | `#0f0f1a` |
| Compute/Data | Cyan | `#00d9ff` |
| Memory | Orange | `#ff6b35` |
| Optimization | Green | `#00ff88` |
| Problems | Red | `#ff4757` |
| Text | Light | `#f0f0f0` |

Typography:
- Main text: Inter / SF Pro
- Code: JetBrains Mono

## Roadmap

- [x] Phase 1: MVP Pipeline
  - [x] Document parsing
  - [x] Mock LLM provider
  - [x] Script generation
  - [x] CLI review interface
  - [x] TTS integration
  - [x] Video composition
  - [x] 112+ tests passing

- [x] Phase 2: First Video
  - [x] Video generation pipeline
  - [x] Motion Canvas integration
  - [x] First video output

- [x] Phase 3: Automated Animation
  - [x] Remotion integration (React-based)
  - [x] Programmatic rendering from scripts
  - [x] Animation components library
  - [x] E2E pipeline working (176s video)
  - [x] 119+ tests passing

- [ ] Phase 4: Production Ready
  - [ ] Real LLM API integration
  - [ ] More animation components
  - [ ] Web interface
  - [ ] Cloud deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [Remotion](https://remotion.dev/) - React-based video generation
- [ElevenLabs](https://elevenlabs.io/) - Text-to-Speech
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Rich](https://rich.readthedocs.io/) - CLI interface
