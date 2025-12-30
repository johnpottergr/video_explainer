"""Persistence for feedback data."""

import json
from pathlib import Path

from .models import FeedbackHistory, FeedbackItem


class FeedbackStore:
    """Handles loading and saving feedback history for a project."""

    FEEDBACK_DIR = "feedback"
    FEEDBACK_FILE = "feedback.json"

    def __init__(self, project_root: Path, project_id: str | None = None):
        """Initialize the feedback store.

        Args:
            project_root: Root directory of the project
            project_id: Project identifier (defaults to directory name)
        """
        self.project_root = Path(project_root)
        self.project_id = project_id or self.project_root.name
        self.feedback_dir = self.project_root / self.FEEDBACK_DIR
        self.feedback_file = self.feedback_dir / self.FEEDBACK_FILE

    def load(self) -> FeedbackHistory:
        """Load feedback history from disk.

        Returns:
            FeedbackHistory object (empty if file doesn't exist)
        """
        if not self.feedback_file.exists():
            return FeedbackHistory(project_id=self.project_id)

        try:
            data = json.loads(self.feedback_file.read_text())
            return FeedbackHistory.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            # Return empty history if file is corrupted
            return FeedbackHistory(project_id=self.project_id)

    def save(self, history: FeedbackHistory) -> None:
        """Save feedback history to disk.

        Args:
            history: The feedback history to save
        """
        # Ensure directory exists
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

        # Write with pretty formatting
        data = history.model_dump(mode="json")
        self.feedback_file.write_text(
            json.dumps(data, indent=2, default=str)
        )

    def add_feedback(self, text: str) -> FeedbackItem:
        """Add new feedback and save.

        Args:
            text: The feedback text

        Returns:
            The newly created FeedbackItem
        """
        history = self.load()
        item = history.add(text)
        self.save(history)
        return item

    def update_item(self, item: FeedbackItem) -> bool:
        """Update a feedback item and save.

        Args:
            item: The updated feedback item

        Returns:
            True if item was updated, False if not found
        """
        history = self.load()
        if history.update_item(item):
            self.save(history)
            return True
        return False

    def get_item(self, item_id: str) -> FeedbackItem | None:
        """Get a feedback item by ID.

        Args:
            item_id: The feedback item ID

        Returns:
            The FeedbackItem or None if not found
        """
        history = self.load()
        return history.get_by_id(item_id)

    def exists(self) -> bool:
        """Check if feedback file exists.

        Returns:
            True if feedback file exists
        """
        return self.feedback_file.exists()
