"""Main CLI entry point for video explainer pipeline.

Usage:
    python -m src.cli list                                    # List all projects
    python -m src.cli info <project>                          # Show project info
    python -m src.cli voiceover <project>                     # Generate voiceovers
    python -m src.cli storyboard <project>                    # Generate storyboard
    python -m src.cli render <project>                        # Render video
    python -m src.cli render <project> --preview              # Quick preview render
    python -m src.cli feedback <project> add "<text>"         # Process feedback
    python -m src.cli feedback <project> add "<text>" --dry-run  # Analyze only
    python -m src.cli feedback <project> list                 # List feedback
    python -m src.cli feedback <project> show <feedback_id>   # Show feedback details
"""

import argparse
import json
import sys
from pathlib import Path


def cmd_list(args: argparse.Namespace) -> int:
    """List all available projects."""
    from ..project import list_projects

    projects = list_projects(args.projects_dir)

    if not projects:
        print(f"No projects found in {args.projects_dir}/")
        return 0

    print(f"Found {len(projects)} project(s):\n")
    for project in projects:
        print(f"  {project.id}")
        print(f"    Title: {project.title}")
        print(f"    Path: {project.root_dir}")
        print()

    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Show detailed project information."""
    from ..project import load_project

    try:
        project = load_project(Path(args.projects_dir) / args.project)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Project: {project.id}")
    print(f"Title: {project.title}")
    print(f"Description: {project.description}")
    print(f"Version: {project.version}")
    print(f"Path: {project.root_dir}")
    print()

    print("Video Settings:")
    print(f"  Resolution: {project.video.width}x{project.video.height}")
    print(f"  FPS: {project.video.fps}")
    print(f"  Target Duration: {project.video.target_duration_seconds}s")
    print()

    print("TTS Settings:")
    print(f"  Provider: {project.tts.provider}")
    print(f"  Voice ID: {project.tts.voice_id}")
    print()

    # Check what files exist
    print("Files:")
    narration_path = project.get_path("narration")
    print(f"  Narrations: {'[exists]' if narration_path.exists() else '[missing]'} {narration_path}")

    voiceover_files = project.get_voiceover_files()
    print(f"  Voiceovers: {len(voiceover_files)} audio files")

    storyboard_path = project.get_path("storyboard")
    print(f"  Storyboard: {'[exists]' if storyboard_path.exists() else '[missing]'} {storyboard_path}")

    output_files = list(project.output_dir.glob("*.mp4"))
    print(f"  Output: {len(output_files)} video files")

    return 0


def cmd_voiceover(args: argparse.Namespace) -> int:
    """Generate voiceovers for a project."""
    from ..project import load_project
    from ..audio import get_tts_provider
    from ..config import Config, TTSConfig

    try:
        project = load_project(Path(args.projects_dir) / args.project)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Load narrations
    try:
        narrations = project.load_narrations()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Generating voiceovers for {project.id}")
    print(f"Found {len(narrations)} scenes")
    print()

    # Determine TTS provider
    provider_name = args.provider or project.tts.provider
    if args.mock:
        provider_name = "mock"

    print(f"Using TTS provider: {provider_name}")

    # Create TTS config
    config = Config()
    config.tts.provider = provider_name
    if project.tts.voice_id:
        config.tts.voice_id = project.tts.voice_id

    tts = get_tts_provider(config)

    # Generate voiceovers
    output_dir = project.voiceover_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    total_duration = 0.0

    for narration in narrations:
        print(f"  Generating: {narration.title}...")
        output_path = output_dir / f"{narration.scene_id}.mp3"

        try:
            result = tts.generate_with_timestamps(narration.narration, output_path)
            results.append({
                "scene_id": narration.scene_id,
                "audio_path": str(output_path),
                "duration_seconds": result.duration_seconds,
                "word_timestamps": [
                    {
                        "word": ts.word,
                        "start_seconds": ts.start_seconds,
                        "end_seconds": ts.end_seconds,
                    }
                    for ts in result.word_timestamps
                ],
            })
            total_duration += result.duration_seconds
            print(f"    Duration: {result.duration_seconds:.2f}s")
        except Exception as e:
            print(f"    Error: {e}", file=sys.stderr)
            if not args.continue_on_error:
                return 1

    # Save manifest
    manifest = {
        "scenes": results,
        "total_duration_seconds": total_duration,
        "output_dir": str(output_dir),
    }

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print()
    print(f"Generated {len(results)} voiceovers")
    print(f"Total duration: {total_duration:.2f}s ({total_duration/60:.1f} min)")
    print(f"Manifest saved to: {manifest_path}")

    return 0


def cmd_storyboard(args: argparse.Namespace) -> int:
    """Generate or view storyboard for a project."""
    from ..project import load_project

    try:
        project = load_project(Path(args.projects_dir) / args.project)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    storyboard_path = project.get_path("storyboard")

    if args.view:
        # View existing storyboard
        if not storyboard_path.exists():
            print(f"Error: Storyboard not found: {storyboard_path}", file=sys.stderr)
            return 1

        with open(storyboard_path) as f:
            storyboard = json.load(f)

        print(f"Storyboard: {storyboard.get('title', 'Untitled')}")
        print(f"Duration: {storyboard.get('duration_seconds', 0)}s")
        print(f"Beats: {len(storyboard.get('beats', []))}")
        print()

        for i, beat in enumerate(storyboard.get("beats", []), 1):
            print(f"  Beat {i}: {beat.get('id', 'unnamed')}")
            print(f"    Time: {beat.get('start_seconds', 0):.1f}s - {beat.get('end_seconds', 0):.1f}s")
            print(f"    Elements: {len(beat.get('elements', []))}")

        return 0

    # Generate storyboard (placeholder - would use LLM)
    print("Storyboard generation from LLM not yet implemented.")
    print("Use --view to view existing storyboard.")
    return 0


# Resolution presets
RESOLUTION_PRESETS = {
    "4k": (3840, 2160),
    "1440p": (2560, 1440),
    "1080p": (1920, 1080),
    "720p": (1280, 720),
    "480p": (854, 480),
}


def cmd_render(args: argparse.Namespace) -> int:
    """Render video for a project."""
    import subprocess

    from ..project import load_project

    try:
        project = load_project(Path(args.projects_dir) / args.project)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Rendering video for {project.id}")

    # Determine composition and setup
    remotion_dir = Path(__file__).parent.parent.parent / "remotion"
    render_script = remotion_dir / "scripts" / "render.mjs"

    if not render_script.exists():
        print(f"Error: Render script not found: {render_script}", file=sys.stderr)
        return 1

    # Check for storyboard
    storyboard_path = project.get_path("storyboard")
    if not storyboard_path.exists():
        print(f"Error: Storyboard not found: {storyboard_path}", file=sys.stderr)
        print("Run storyboard generation first or create storyboard/storyboard.json")
        return 1

    # Check for voiceover files
    voiceover_files = list(project.voiceover_dir.glob("*.mp3"))
    print(f"Found {len(voiceover_files)} voiceover files")

    # Determine resolution
    resolution_name = args.resolution or "1080p"
    if resolution_name not in RESOLUTION_PRESETS:
        print(f"Error: Unknown resolution '{resolution_name}'", file=sys.stderr)
        print(f"Available: {', '.join(RESOLUTION_PRESETS.keys())}", file=sys.stderr)
        return 1
    width, height = RESOLUTION_PRESETS[resolution_name]

    # Determine output path
    if args.preview:
        output_path = project.output_dir / "preview" / "preview.mp4"
    else:
        # Include resolution in filename for non-1080p renders
        if resolution_name != "1080p":
            output_path = project.output_dir / f"final-{resolution_name}.mp4"
        else:
            output_path = project.get_path("final_video")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build render command using new data-driven architecture
    # The render script uses the project directory to serve static files (voiceovers)
    cmd = [
        "node",
        str(render_script),
        "--project", str(project.root_dir),
        "--output", str(output_path),
        "--width", str(width),
        "--height", str(height),
    ]

    print(f"Project: {project.root_dir}")
    print(f"Resolution: {resolution_name} ({width}x{height})")
    print(f"Output: {output_path}")
    print(f"Running: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, cwd=str(remotion_dir))
        if result.returncode != 0:
            print(f"Render failed with exit code {result.returncode}", file=sys.stderr)
            return result.returncode
    except FileNotFoundError:
        print("Error: Node.js not found. Please install Node.js.", file=sys.stderr)
        return 1

    print()
    print(f"Video rendered to: {output_path}")
    return 0


def cmd_feedback(args: argparse.Namespace) -> int:
    """Process or view feedback for a project."""
    from ..project import load_project
    from ..feedback import FeedbackProcessor, FeedbackStore

    try:
        project = load_project(Path(args.projects_dir) / args.project)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not args.feedback_command:
        print("Usage: python -m src.cli feedback <project> <command>")
        print("\nCommands:")
        print("  add <text>     Add and process new feedback")
        print("  list           List all feedback for the project")
        print("  show <id>      Show details of a feedback item")
        return 1

    if args.feedback_command == "add":
        # Process new feedback
        processor = FeedbackProcessor(
            project,
            dry_run=args.dry_run,
            create_branch=not args.no_branch,
        )

        print(f"Processing feedback for {project.id}...")
        print(f"Feedback: {args.feedback_text}")
        print()

        if args.dry_run:
            print("[DRY RUN] Analyzing feedback only, no changes will be made")
            print()

        item = processor.process_feedback(args.feedback_text)

        print(f"Feedback ID: {item.id}")
        print(f"Status: {item.status}")

        if item.interpretation:
            print(f"\nInterpretation:")
            print(f"  {item.interpretation}")

        if item.scope:
            print(f"\nScope: {item.scope}")
            if item.affected_scenes:
                print(f"Affected scenes: {', '.join(item.affected_scenes)}")

        if item.suggested_changes:
            print(f"\nSuggested changes:")
            desc = item.suggested_changes.get("description", "")
            if desc:
                print(f"  {desc}")
            files = item.suggested_changes.get("files_to_modify", [])
            if files:
                print(f"  Files: {', '.join(files)}")

        if item.preview_branch:
            print(f"\nPreview branch: {item.preview_branch}")
            print("  To review: git diff main")
            print("  To merge: git checkout main && git merge " + item.preview_branch)
            print("  To discard: git checkout main && git branch -D " + item.preview_branch)

        if item.files_modified:
            print(f"\nFiles modified:")
            for f in item.files_modified:
                print(f"  - {f}")

        if item.error_message:
            print(f"\nError: {item.error_message}", file=sys.stderr)

        return 0 if item.status != "failed" else 1

    elif args.feedback_command == "list":
        # List all feedback
        store = FeedbackStore(project.root_dir, project.id)
        history = store.load()

        if not history.items:
            print(f"No feedback found for {project.id}")
            return 0

        print(f"Feedback for {project.id} ({len(history.items)} items):\n")

        for item in history.items:
            status_icon = {
                "pending": "⏳",
                "processing": "🔄",
                "applied": "✅",
                "rejected": "❌",
                "failed": "💥",
            }.get(item.status, "?")

            print(f"  {status_icon} {item.id}")
            print(f"    Status: {item.status}")
            print(f"    Feedback: {item.feedback_text[:60]}{'...' if len(item.feedback_text) > 60 else ''}")
            if item.affected_scenes:
                print(f"    Scenes: {', '.join(item.affected_scenes)}")
            print()

        return 0

    elif args.feedback_command == "show":
        # Show detailed feedback
        store = FeedbackStore(project.root_dir, project.id)
        item = store.get_item(args.feedback_id)

        if not item:
            print(f"Error: Feedback not found: {args.feedback_id}", file=sys.stderr)
            return 1

        print(f"Feedback: {item.id}")
        print(f"Status: {item.status}")
        print(f"Timestamp: {item.timestamp}")
        print()
        print("Original feedback:")
        print(f"  {item.feedback_text}")
        print()

        if item.interpretation:
            print("Interpretation:")
            print(f"  {item.interpretation}")
            print()

        if item.scope:
            print(f"Scope: {item.scope}")
        if item.affected_scenes:
            print(f"Affected scenes: {', '.join(item.affected_scenes)}")
        print()

        if item.suggested_changes:
            print("Suggested changes:")
            print(json.dumps(item.suggested_changes, indent=2))
            print()

        if item.preview_branch:
            print(f"Preview branch: {item.preview_branch}")

        if item.files_modified:
            print("Files modified:")
            for f in item.files_modified:
                print(f"  - {f}")

        if item.error_message:
            print(f"\nError: {item.error_message}")

        return 0

    return 0


def cmd_create(args: argparse.Namespace) -> int:
    """Create a new project."""
    from ..project.loader import create_project

    try:
        project = create_project(
            project_id=args.project_id,
            title=args.title or args.project_id.replace("-", " ").title(),
            projects_dir=args.projects_dir,
            description=args.description or "",
        )
        print(f"Created project: {project.id}")
        print(f"Path: {project.root_dir}")
        print()
        print("Next steps:")
        print(f"  1. Add source document to {project.input_dir}/")
        print(f"  2. Add narrations to {project.narration_dir}/narrations.json")
        print(f"  3. Run: python -m src.cli voiceover {project.id}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Video Explainer Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--projects-dir",
        default="projects",
        help="Path to projects directory (default: projects)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list command
    list_parser = subparsers.add_parser("list", help="List all projects")
    list_parser.set_defaults(func=cmd_list)

    # info command
    info_parser = subparsers.add_parser("info", help="Show project information")
    info_parser.add_argument("project", help="Project ID")
    info_parser.set_defaults(func=cmd_info)

    # create command
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("project_id", help="Project ID (used as directory name)")
    create_parser.add_argument("--title", help="Project title")
    create_parser.add_argument("--description", help="Project description")
    create_parser.set_defaults(func=cmd_create)

    # voiceover command
    voiceover_parser = subparsers.add_parser("voiceover", help="Generate voiceovers")
    voiceover_parser.add_argument("project", help="Project ID")
    voiceover_parser.add_argument(
        "--provider",
        choices=["elevenlabs", "edge", "mock"],
        help="TTS provider to use",
    )
    voiceover_parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock TTS (for testing)",
    )
    voiceover_parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue even if some scenes fail",
    )
    voiceover_parser.set_defaults(func=cmd_voiceover)

    # storyboard command
    storyboard_parser = subparsers.add_parser("storyboard", help="Generate or view storyboard")
    storyboard_parser.add_argument("project", help="Project ID")
    storyboard_parser.add_argument(
        "--view",
        action="store_true",
        help="View existing storyboard instead of generating",
    )
    storyboard_parser.set_defaults(func=cmd_storyboard)

    # render command
    render_parser = subparsers.add_parser("render", help="Render video")
    render_parser.add_argument("project", help="Project ID")
    render_parser.add_argument(
        "--preview",
        action="store_true",
        help="Quick preview render",
    )
    render_parser.add_argument(
        "--resolution", "-r",
        choices=["4k", "1440p", "1080p", "720p", "480p"],
        default="1080p",
        help="Output resolution (default: 1080p)",
    )
    render_parser.set_defaults(func=cmd_render)

    # feedback command
    feedback_parser = subparsers.add_parser(
        "feedback",
        help="Process or view feedback for a project",
    )
    feedback_parser.add_argument("project", help="Project ID")

    feedback_subparsers = feedback_parser.add_subparsers(
        dest="feedback_command",
        help="Feedback commands",
    )

    # feedback add
    feedback_add_parser = feedback_subparsers.add_parser(
        "add",
        help="Add and process new feedback",
    )
    feedback_add_parser.add_argument(
        "feedback_text",
        help="The feedback text (natural language)",
    )
    feedback_add_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze feedback without applying changes",
    )
    feedback_add_parser.add_argument(
        "--no-branch",
        action="store_true",
        help="Don't create a preview branch",
    )

    # feedback list
    feedback_subparsers.add_parser(
        "list",
        help="List all feedback for the project",
    )

    # feedback show
    feedback_show_parser = feedback_subparsers.add_parser(
        "show",
        help="Show details of a feedback item",
    )
    feedback_show_parser.add_argument(
        "feedback_id",
        help="Feedback ID (e.g., fb_0001_1234567890)",
    )

    feedback_parser.set_defaults(func=cmd_feedback)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
