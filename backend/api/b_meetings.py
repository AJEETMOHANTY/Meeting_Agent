
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool

from backend.meeting.a_main import graph
from backend.database.a_connection import SessionLocal
from backend.database.c_crud import get_all_meetings,get_decisions_by_meeting_id,get_tasks_by_meeting_id
from backend.database.c_crud import delete_meeting
from backend.database.c_crud import (
    get_all_meetings,
    get_decisions_by_meeting_id,
    get_tasks_by_meeting_id,
    delete_meeting,
    update_meeting,
)
from pydantic import BaseModel, Field


router = APIRouter(prefix="/meetings", tags=["Meetings"])

# Supported audio formats for the first version.
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a",".mp4"}


@router.post("/upload")
async def upload_meeting(file: UploadFile = File(...)):

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only MP3, WAV, and M4A files are supported."
        )

    # Temporarily store the uploaded audio for Whisper.
    # The temporary file is deleted after processing.
    with NamedTemporaryFile(
        suffix=extension,
        delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        # Copy uploaded audio to the temporary file.
        with temp_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                output.write(chunk)

        # Initialize the existing meeting pipeline.
        initial_state = {
            "audio_path": str(temp_path),
            "transcript": "",
            "summary": "",
            "decisions": [],
            "tasks": [],
        }

        # Run the existing LangGraph pipeline.
        result = await run_in_threadpool(graph.invoke, initial_state)

        # Return the processed meeting information.
        return {
            "meeting_id": result.get("meeting_id"),
            "message": "Meeting processed successfully",
            "summary": result["summary"],
            "decisions": result["decisions"],
            "tasks": result["tasks"],
        }

    finally:
        temp_path.unlink(missing_ok=True)
        await file.close()
        

# Retrieves all saved meetings, including their decisions and tasks.
@router.get("/")
def get_meetings():
    db = SessionLocal()

    try:
        meetings = get_all_meetings(db)
        meeting_list = []

        # Loads each meeting and its related information.
        for meeting in meetings:
            decisions = get_decisions_by_meeting_id(db, meeting.id)
            tasks = get_tasks_by_meeting_id(db, meeting.id)

            meeting_list.append({
                "meeting_id": meeting.id,
                "title": meeting.title,
                "summary": meeting.summary,
                "created_at": (
                    meeting.created_at.isoformat()
                    if meeting.created_at
                    else None
                ),
                "decisions": [
                    decision.decision for decision in decisions
                ],
                "tasks": [
                    {
                        "id": task.id,
                        "task": task.task,
                        "owner": task.owner,
                        "deadline_date": (
                            task.deadline_date.isoformat()
                            if task.deadline_date
                            else None
                        ),
                        "priority": task.priority,
                        "status": task.status,
                    }
                    for task in tasks
                ],
            })

        return meeting_list

    finally:
        db.close()

class MeetingTitleUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=150)

@router.patch("/{meeting_id}/title")
def rename_meeting(meeting_id: int, request: MeetingTitleUpdate):
    title = request.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Meeting title cannot be empty.",
        )

    db = SessionLocal()

    try:
        meeting = update_meeting(db, meeting_id, title)

        if meeting is None:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found.",
            )

        return {
            "meeting_id": meeting.id,
            "title": meeting.title,
            "message": "Meeting title updated successfully.",
        }
    finally:
        db.close()


@router.delete("/{meeting_id}")
def remove_meeting(meeting_id: int):
    db = SessionLocal()
    try:
        meeting = delete_meeting(db, meeting_id)

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found",
            )

        return {
            "message": "Meeting deleted successfully",
            "meeting_id": meeting_id,
        }
    finally:
        db.close()
