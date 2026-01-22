# Sound Design

The sound design system provides frame-accurate SFX, AI-generated background music, and audio mixing capabilities.

## Overview

Sound design enhances videos with:
- **SFX (Sound Effects)** - Subtle sounds synced to animations
- **Background Music** - AI-generated ambient music via MusicGen
- **Audio Mixing** - Combining voiceover, SFX, and music

## Quick Start

```bash
# Generate SFX library
python -m src.cli sound <project> library --generate

# Analyze scenes for sound moments
python -m src.cli sound <project> analyze

# Generate SFX cues automatically
python -m src.cli sound <project> generate

# Generate background music
python -m src.cli music <project> generate
```

---

## SFX System

### Sound Library

The system includes 10 professionally-designed sounds:

| Sound | Description | Use Case |
|-------|-------------|----------|
| `ui_pop` | Soft digital pop | Elements appearing |
| `text_tick` | Light keyboard click | Text appearing |
| `lock_click` | Crisp mechanical click | Things locking into place |
| `data_flow` | Subtle digital stream | Data movement |
| `counter_sweep` | Rising electronic sweep | Number counters |
| `reveal_hit` | Punchy impact | Big reveals (87x faster, etc) |
| `warning_tone` | Low rumble | Problem states |
| `success_tone` | Positive chime | Solutions and success |
| `transition_whoosh` | Smooth sweep | Phase transitions |
| `cache_click` | Solid digital click | Cache/memory operations |

```bash
# List available sounds
python -m src.cli sound <project> library --list

# Generate all sound files to project's sfx/ directory
python -m src.cli sound <project> library --generate
```

### Automatic SFX Generation

The system can automatically analyze scene code and generate SFX cues:

```bash
# Preview what would be detected (dry run)
python -m src.cli sound <project> analyze
python -m src.cli sound <project> analyze --verbose  # Show detailed moments

# Generate cues and write to storyboard.json
python -m src.cli sound <project> generate
python -m src.cli sound <project> generate --dry-run  # Preview without writing

# Clear all SFX cues
python -m src.cli sound <project> clear
```

### Detection Patterns

The analyzer detects these animation patterns in TSX code:

| Pattern | Sound Type | Detection |
|---------|------------|-----------|
| Opacity fade in | `element_appear` | `interpolate(frame, [X,Y], [0,1])` |
| Opacity fade out | `element_disappear` | `interpolate(frame, [X,Y], [1,0])` |
| Spring animations | `element_appear` | `spring({...})` |
| Counter animations | `counter` | `Math.round(interpolate(...))` |
| Width/height growth | `chart_grow` | Width/height interpolations |
| Phase transitions | `transition` | Phase constant detection |

### SFX Cue Format

SFX cues are stored in `storyboard.json`:

```json
{
  "scenes": [
    {
      "id": "scene1_hook",
      "sfx_cues": [
        {"sound": "ui_pop", "frame": 15, "volume": 0.08},
        {"sound": "reveal_hit", "frame": 90, "volume": 0.12}
      ]
    }
  ]
}
```

### Volume Guidelines

| Sound Type | Recommended Volume |
|------------|-------------------|
| Text/typing (repeated) | 0.05 |
| UI elements | 0.08 |
| Transitions | 0.08-0.10 |
| Counters | 0.10 |
| Warnings/success | 0.10 |
| Reveals | 0.12-0.15 |

**Rules:**
- Never exceed 0.15 for any sound
- Use lower volumes for repeated sounds in quick succession
- Space repeated sounds at least 15-20 frames apart

---

## AI Background Music

Generate ambient background music using Meta's MusicGen model.

### Full Video Music

```bash
# Generate background music
python -m src.cli music <project> generate

# With options
python -m src.cli music <project> generate --duration 120  # 2 minutes
python -m src.cli music <project> generate --style "ambient electronic"

# Check device support
python -m src.cli music <project> info
```

Output: `projects/<project>/music/background.mp3`

### Shorts Music

Generate punchy, energetic music for shorts:

```bash
python -m src.cli music <project> short
python -m src.cli music <project> short --variant teaser
python -m src.cli music <project> short --style "upbeat electronic, driving bass"
```

**Shorts music features:**
- Analyzes beat captions to detect content mood
- Detects emotional arc (problem → solution, tension, triumphant)
- Uses punchy presets (120 BPM, bold synths, driving rhythm)
- Higher volume (0.35 vs 0.3) for mobile playback

### Mood Detection

| Mood | Trigger | Music Style |
|------|---------|-------------|
| Journey | Problem + solution detected | Building energy, tension to release |
| Tension | Only problems detected | Building tension, suspenseful |
| Triumphant | Only solutions detected | Uplifting, positive energy |
| Energetic | Default | Standard punchy preset |

### Device Support

MusicGen runs on:
- **MPS** (Apple Silicon) - Recommended for Mac
- **CUDA** (NVIDIA GPU) - Best performance
- **CPU** - Fallback, slower

Check your setup:
```bash
python -m src.cli music <project> info
```

---

## Theme-Aware Sound Generation

The generator supports different themes for varied sonic palettes:

| Theme | Character |
|-------|-----------|
| `tech_ai` | Digital, sci-fi, whole-tone scales |
| `science` | Clean, precise, lydian feel |
| `finance` | Professional, warm, pentatonic |
| `space` | Deep, spacey, mysterious intervals |
| `nature` | Organic, warm, natural major |
| `abstract` | Neutral, balanced |

```bash
python -m src.cli sound <project> generate --theme science
```

---

## CLI Reference

### Sound Commands

```bash
python -m src.cli sound <project> <command> [options]
```

| Command | Description |
|---------|-------------|
| `library --list` | List available sounds |
| `library --generate` | Generate all SFX files |
| `analyze` | Preview detected sound moments |
| `generate` | Generate SFX cues to storyboard |
| `clear` | Remove SFX cues from storyboard |

### Generate Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview without writing |
| `--no-llm` | Skip LLM analysis (faster) |
| `--theme` | Sound theme |
| `--max-density` | Max sounds per second (default: 3.0) |
| `--min-gap` | Min frames between sounds (default: 10) |

### Music Commands

```bash
python -m src.cli music <project> <command> [options]
```

| Command | Description |
|---------|-------------|
| `generate` | Generate full video background music |
| `short` | Generate shorts background music |
| `info` | Show device support and presets |

### Music Options

| Option | Description |
|--------|-------------|
| `--duration` | Target duration in seconds |
| `--style` | Custom style prompt |
| `--variant` | Shorts variant name |
