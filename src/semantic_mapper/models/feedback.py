"""
Feedback models.

These capture human feedback on ontology proposals.
Every decision must be tracked and can influence future proposals.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class FeedbackAction(str, Enum):
    """Types of feedback actions."""

    ACCEPT = "accept"
    REJECT = "reject"
    MODIFY = "modify"
    MERGE = "merge"
    SPLIT = "split"
    RENAME = "rename"
    REQUEST_ALTERNATIVE = "request_alternative"
    ADD_CONSTRAINT = "add_constraint"
    QUESTION = "question"


class FeedbackItem(BaseModel):
    """
    A single piece of feedback on a proposal element.
    """

    feedback_id: UUID = Field(default_factory=uuid4)
    proposal_id: UUID
    target_type: str  # "class", "relation", "property", "ontology"
    target_id: UUID  # ID of the specific class/relation/property
    action: FeedbackAction
    comments: str = Field(default="", description="Human explanation of the feedback")
    modifications: Dict[str, Any] = Field(
        default_factory=dict, description="Specific modifications requested"
    )
    guidance_for_next_iteration: str = Field(
        default="", description="Guidance to incorporate in the next proposal"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "user"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump()
        data["feedback_id"] = str(data["feedback_id"])
        data["proposal_id"] = str(data["proposal_id"])
        data["target_id"] = str(data["target_id"])
        data["created_at"] = data["created_at"].isoformat()
        return data


class FeedbackSession(BaseModel):
    """
    A complete feedback session on an ontology proposal.
    """

    session_id: UUID = Field(default_factory=uuid4)
    proposal_id: UUID
    feedback_items: List[FeedbackItem] = Field(default_factory=list)
    overall_decision: str = Field(
        default="in_progress", description="accept, reject, request_revision"
    )
    overall_comments: str = Field(default="")
    iteration_number: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    @property
    def is_complete(self) -> bool:
        """Whether the feedback session is complete."""
        return self.overall_decision in ["accept", "reject"]

    @property
    def accepted(self) -> bool:
        """Whether the proposal was accepted."""
        return self.overall_decision == "accept"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump()
        data["session_id"] = str(data["session_id"])
        data["proposal_id"] = str(data["proposal_id"])
        data["created_at"] = data["created_at"].isoformat()
        if data["completed_at"]:
            data["completed_at"] = data["completed_at"].isoformat()
        return data
