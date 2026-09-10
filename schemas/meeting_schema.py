from typing import List, Optional

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    task: str

    assignee: Optional[str] = None

    deadline: Optional[str] = None

    priority: Optional[str] = None

    status: str = "Pending"


class Participant(BaseModel):
    name: str

    responsibilities: List[str] = Field(
        default_factory=list
    )


class MeetingIntelligence(BaseModel):

    summary: str

    key_points: List[str] = Field(
        default_factory=list
    )

    decisions: List[str] = Field(
        default_factory=list
    )

    action_items: List[ActionItem] = Field(
        default_factory=list
    )

    participants: List[Participant] = Field(
        default_factory=list
    )