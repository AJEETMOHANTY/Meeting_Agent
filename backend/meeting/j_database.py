# ============================================================
# STEP J: DATABASE SAVING
# Saves meeting information and transcript embeddings into PostgreSQL.
# ============================================================
from backend.database.a_connection import SessionLocal
from backend.database.c_crud import create_meeting, create_decision, create_task
from backend.meeting.i_state import MeetingState
from backend.meeting.f_embeddings import MeetingEmbeddings


# Create the embedding handler.
# The model is loaded when this object is initialized.
meeting_embeddings = MeetingEmbeddings()


def save_meeting(state: MeetingState):
    """Save meeting data and transcript embeddings."""

    db = SessionLocal()

    try:
        # 1. Save the meeting and its complete transcript.
        meeting = create_meeting(
            db=db,
            title=state.get("title", "Meeting"),
            transcript=state["transcript"],
            summary=state["summary"],
        )

        # Get the database-generated meeting ID.
        meeting_id = meeting.id

        print(f"Meeting saved with ID: {meeting_id}")

        # 2. Generate embeddings from the actual transcript.
        chunk_texts, vectors = meeting_embeddings.generate_embeddings(
            state["transcript"]
        )

        # 3. Store all transcript chunks and embeddings.
        meeting_embeddings.store_embeddings(
            meeting_id=meeting_id,
            chunk_texts=chunk_texts,
            vectors=vectors,
        )

        # 4. Save decisions.
        for decision in state["decisions"]:
            create_decision(
                db=db,
                meeting_id=meeting_id,
                decision=decision,
            )

        print("Decisions saved.")

        # 5. Save tasks.
        for task in state["tasks"]:
            create_task(
                db=db,
                meeting_id=meeting_id,
                task=task.description,
                owner=task.owner,
                deadline_date=None,
                priority=task.priority,
                status=task.status,
            )

        print("Tasks saved.")

        # Return the meeting ID to the calling pipeline.
        return {"meeting_id": meeting_id}

    finally:
        db.close()