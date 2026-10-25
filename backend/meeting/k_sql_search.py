# ============================================================
# SQL RETRIEVAL TOOL: Retrieves structured meeting information from PostgreSQL. This will later be used by our Agentic RAG system.
# ============================================================

from backend.database.a_connection import SessionLocal

from backend.database.c_crud import (
    get_all_meetings,
    get_all_tasks,
    get_tasks_by_meeting_id,
    get_decisions_by_meeting_id,
)


def search_meetings():
    """Retrieve all meetings."""

    db = SessionLocal()

    try:
        meetings = get_all_meetings(db)

        return [
            {
                "meeting_id": meeting.id,
                "title": meeting.title,
                "summary": meeting.summary,
            }
            for meeting in meetings
        ]

    finally:
        db.close()


def search_tasks(status: str = None, meeting_id: int = None):
    """Retrieve tasks, optionally filtered by status or meeting."""

    db = SessionLocal()

    try:
        tasks = (
            get_tasks_by_meeting_id(db, meeting_id)
            if meeting_id is not None
            else get_all_tasks(db)
        )

        # Apply the status filter.
        if status is not None:
            tasks = [task for task in tasks if task.status == status]

        return [
            {
                "task_id": task.id,
                "meeting_id": task.meeting_id,
                "task": task.task,
                "owner": task.owner,
                "priority": task.priority,
                "status": task.status,
                "deadline_date": (
                    task.deadline_date.isoformat() if task.deadline_date else None
                ),
            }
            for task in tasks
        ]

    finally:
        db.close()


def search_decisions(meeting_id: int):
    """Retrieve decisions for a specific meeting."""

    db = SessionLocal()

    try:
        decisions = get_decisions_by_meeting_id(db, meeting_id)

        return [
            {
                "meeting_id": decision.meeting_id,
                "decision": decision.decision,
            }
            for decision in decisions
        ]

    finally:
        db.close()


# ============================================================
# TEST SQL RETRIEVAL
# ============================================================

if __name__ == "__main__":

    print("\nMEETINGS")
    print(search_meetings())

    print("\nPENDING TASKS")
    print(search_tasks(status="pending"))

    print("\nDECISIONS FROM MEETING 4")
    print(search_decisions(meeting_id=4))
