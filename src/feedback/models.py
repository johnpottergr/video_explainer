"""Data models for the feedback system."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FeedbackStatus(str, Enum):
    """Status of a feedback item."""

    PENDING = "pending"
    PROCESSING = "processing"
    APPLIED = "applied"
    REJECTED = "rejected"
    FAILED = "failed"


class FeedbackScope(str, Enum):
    """Scope of changes for a feedback item."""

    SCENE = "scene"
    STORYBOARD = "storyboard"
    PROJECT = "project"


class FeedbackItem(BaseModel):
    """A single feedback item with its processing state."""

    id: str = Field(description="Unique identifier for this feedback")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the feedback was submitted",
    )
    feedback_text: str = Field(description="Original feedback from user")
    status: FeedbackStatus = Field(
        default=FeedbackStatus.PENDING,
        description="Current processing status",
    )
    scope: FeedbackScope | None = Field(
        default=None,
        description="Scope of the changes (scene, storyboard, project)",
    )
    affected_scenes: list[str] = Field(
        default_factory=list,
        description="List of scene IDs affected by this feedback",
    )
    interpretation: str = Field(
        default="",
        description="LLM interpretation of the feedback",
    )
    suggested_changes: dict[str, Any] = Field(
        default_factory=dict,
        description="Proposed changes from the LLM",
    )
    files_modified: list[str] = Field(
        default_factory=list,
        description="Files that were modified when applying feedback",
    )
    preview_branch: str | None = Field(
        default=None,
        description="Git branch name for preview changes",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if processing failed",
    )

    model_config = {"use_enum_values": True}


class FeedbackHistory(BaseModel):
    """Collection of feedback items for a project."""

    project_id: str = Field(description="Project this feedback belongs to")
    items: list[FeedbackItem] = Field(
        default_factory=list,
        description="List of feedback items",
    )

    def add(self, feedback_text: str) -> FeedbackItem:
        """Add a new feedback item.

        Args:
            feedback_text: The feedback text from the user

        Returns:
            The newly created FeedbackItem
        """
        # Generate unique ID based on count and timestamp
        count = len(self.items) + 1
        timestamp = datetime.now()
        item_id = f"fb_{count:04d}_{int(timestamp.timestamp())}"

        item = FeedbackItem(
            id=item_id,
            timestamp=timestamp,
            feedback_text=feedback_text,
        )
        self.items.append(item)
        return item

    def get_pending(self) -> list[FeedbackItem]:
        """Get all pending feedback items.

        Returns:
            List of feedback items with PENDING status
        """
        return [item for item in self.items if item.status == FeedbackStatus.PENDING]

    def get_by_id(self, item_id: str) -> FeedbackItem | None:
        """Get a feedback item by ID.

        Args:
            item_id: The feedback item ID

        Returns:
            The FeedbackItem or None if not found
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def update_item(self, item: FeedbackItem) -> bool:
        """Update an existing feedback item.

        Args:
            item: The updated feedback item

        Returns:
            True if item was found and updated, False otherwise
        """
        for i, existing in enumerate(self.items):
            if existing.id == item.id:
                self.items[i] = item
                return True
        return False

    def get_applied(self) -> list[FeedbackItem]:
        """Get all successfully applied feedback items.

        Returns:
            List of feedback items with APPLIED status
        """
        return [item for item in self.items if item.status == FeedbackStatus.APPLIED]

    def get_failed(self) -> list[FeedbackItem]:
        """Get all failed feedback items.

        Returns:
            List of feedback items with FAILED status
        """
        return [item for item in self.items if item.status == FeedbackStatus.FAILED]
