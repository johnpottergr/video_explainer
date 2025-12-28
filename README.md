# Video Explainer System

A powerful system for generating high-quality explainer videos from technical documents. Transform research papers, articles, and documentation into engaging video content with automated narration and animations.

## Features

- **Document Parsing**: Parse Markdown documents with code blocks, equations, and images
- **Content Analysis**: Automatically extract key concepts and structure content for video
- **Script Generation**: Generate video scripts with visual cues and voiceover text
- **Text-to-Speech**: Integration with ElevenLabs TTS (with mock mode for development)
- **Motion Canvas Animations**: TypeScript-based animations for technical visualizations
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

# Install Node.js dependencies for animations
cd animations
npm install
cd ..
```

### Generate Your First Video

```bash
# Using mock data (no API costs)
python generate_video.py

# Or use the pipeline directly
python -c "
from src.pipeline import VideoPipeline
pipeline = VideoPipeline()
result = pipeline.quick_test()
print(f'Video created: {result.output_path}')
"
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
│   │   └── renderer.py     # Motion Canvas renderer
│   ├── composition/        # Video assembly
│   │   └── composer.py     # FFmpeg-based video composer
│   ├── pipeline/           # End-to-end orchestration
│   │   └── orchestrator.py # Video generation pipeline
│   ├── config.py           # Configuration management
│   └── models.py           # Pydantic data models
├── animations/             # Motion Canvas project
│   ├── src/scenes/         # Animation scenes
│   │   └── prefillDecode.tsx
│   └── src/styles/         # Color palette, fonts
├── tests/                  # Test suite (112 tests)
├── output/                 # Generated assets
├── Dockerfile              # Container setup
└── generate_video.py       # Quick generation script
```

## Pipeline Architecture

```
Source Document → Parse → Analyze → Generate Script → Review → TTS → Animate → Compose → Video
       │            │         │            │            │        │        │          │
   Markdown      Sections   Concepts    Scenes      Approval   Audio   Video     Final
     PDF         Headings   Insights    Visual       Edits     Files   Frames    MP4
     URL         Code       Thesis      Cues
```

## Usage Examples

### Generate Video from Document

```python
from src.pipeline import VideoPipeline
from src.config import Config

# Configure for mock mode (development)
config = Config()
config.llm.provider = "mock"
config.tts.provider = "mock"

# Create pipeline
pipeline = VideoPipeline(config=config, output_dir="output")

# Set up progress callback
def on_progress(stage, percent):
    print(f"[{stage}] {percent:.0f}%")

pipeline.set_progress_callback(on_progress)

# Generate video
result = pipeline.generate_from_document(
    "path/to/document.md",
    target_duration=180,  # 3 minutes
    use_mock=True
)

if result.success:
    print(f"Video created: {result.output_path}")
    print(f"Duration: {result.duration_seconds}s")
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
config.llm.provider = "mock"  # Use mock for testing
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

### Review Script via CLI

```python
from src.review import ReviewCLI
from src.script import ScriptGenerator

script = ScriptGenerator.load_script("output/scripts/my_video.json")
cli = ReviewCLI()

# Display and get user feedback
result = cli.review_script(script)
if result.approved:
    print("Script approved!")
elif result.edited:
    print(f"Script edited: {result.changes}")
```

## Configuration

Configuration is managed through `config.yaml`:

```yaml
llm:
  provider: mock  # mock | openai | anthropic
  model: gpt-4
  temperature: 0.7

tts:
  provider: mock  # mock | elevenlabs
  voice_id: null  # Uses default voice if not specified
  model: eleven_turbo_v2

video:
  width: 1920
  height: 1080
  fps: 30
  format: mp4
```

Environment variables for API keys:
- `OPENAI_API_KEY` - For OpenAI LLM provider
- `ANTHROPIC_API_KEY` - For Claude LLM provider
- `ELEVENLABS_API_KEY` - For ElevenLabs TTS

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pipeline.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
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

### Motion Canvas Animations

Start the Motion Canvas editor:

```bash
cd animations
npm run dev
```

This opens a web-based editor at `http://localhost:9000` where you can preview and develop animations.

### Creating New Animations

Add new scenes in `animations/src/scenes/`:

```typescript
import {makeScene2D, Rect, Txt} from '@motion-canvas/2d';
import {createRef, all} from '@motion-canvas/core';
import {Colors, Fonts} from '../styles/colors';

export default makeScene2D(function* (view) {
  const title = createRef<Txt>();

  view.add(
    <Txt
      ref={title}
      text="My Animation"
      fontSize={64}
      fontFamily={Fonts.main}
      fill={Colors.text}
    />
  );

  yield* title().opacity(0).to(1, 0.5);
});
```

Register in `animations/src/project.ts`:

```typescript
import {makeProject} from '@motion-canvas/core';
import myScene from './scenes/myScene?scene';

export default makeProject({
  scenes: [myScene],
});
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
  - [x] Motion Canvas setup
  - [x] TTS integration
  - [x] Video composition
  - [x] 112 tests passing

- [x] Phase 2: First Video
  - [x] Video generation pipeline
  - [x] Mock rendering
  - [x] First video output

- [ ] Phase 3: Production
  - [ ] Real LLM API integration
  - [ ] Real Motion Canvas rendering
  - [ ] Multiple animation scenes
  - [ ] Real TTS integration
  - [ ] Web interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [Motion Canvas](https://motioncanvas.io/) - Animation framework
- [ElevenLabs](https://elevenlabs.io/) - Text-to-Speech
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Rich](https://rich.readthedocs.io/) - CLI interface
