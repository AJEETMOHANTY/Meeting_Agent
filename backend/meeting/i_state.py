from typing import TypedDict, Optional, Literal
from pydantic import BaseModel
from datetime import date


# ============================================================
# TASK: Represents one action item identified from the meeting.
# ============================================================
class Task(BaseModel):

    description: str

    # Person responsible for the task, if mentioned.
    owner: Optional[str] = None

    # Deadline date, if mentioned.
    deadline_date: Optional[date] = None

    # Priority, if explicitly mentioned.
    priority: Optional[Literal["low", "medium", "high"]] = None

    # Current task status.
    status: Literal["pending", "in_progress", "completed"] = "pending"


# ============================================================
# MEETING KNOWLEDGE: This is the structured output we want from Gemini.
# ============================================================
class MeetingKnowledge(BaseModel):

    summary: str
    decisions: list[str]
    tasks: list[Task]


# ============================================================
# LANGGRAPH STATE: This is the information passed between pipeline nodes.
# ============================================================
class MeetingState(TypedDict):

    audio_path: str
    transcript: str
    summary: str
    decisions: list[str]
    tasks: list
