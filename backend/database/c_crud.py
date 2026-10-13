# ============================================================
# DATABASE CRUD OPERATIONS
#
# This file contains the Python functions that use
# SQLAlchemy to create, read, update, and delete data.
#
# Python Code
#     ↓
# CRUD Function
#     ↓
# SQLAlchemy
#     ↓
# PostgreSQL
# ============================================================

from sqlalchemy.orm import Session
from backend.database.b_models import Meeting, Task, Decision

# ============================================================
# MEETING CRUD:
# create_meeting(): Creates and saves a new meeting in the database.
# get_meeting_by_id(): Finds one meeting using its ID.
# get_all_meetings(): Gets all meetings stored in the database.
# count_meetings(): Counts how many meetings exist.
# update_meeting(): Changes the title of an existing meeting.
# delete_meeting(): Deletes a meeting from the database.
# ============================================================

# ==========================
# CREATE MEETING
# ==========================
def create_meeting(db: Session, title: str, transcript: str, summary: str):

    meeting = Meeting(title=title, transcript=transcript, summary=summary)

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return meeting

# ==========================
# GET MEETING BY ID
# ==========================
def get_meeting_by_id(db: Session, meeting_id: int):
    return db.query(Meeting).filter(Meeting.id == meeting_id).first()

# ==========================
# GET ALL MEETINGS
# ==========================
def get_all_meetings(db: Session):
    return db.query(Meeting).all()

# ==========================
# COUNT MEETINGS
# ==========================
def count_meetings(db: Session):
    return db.query(Meeting).count()

# ==========================
# UPDATE MEETING
# ==========================
def update_meeting(db: Session, meeting_id: int, title: str):
    meeting = get_meeting_by_id(db, meeting_id)

    if meeting is None:
        return None

    meeting.title = title

    db.commit()
    db.refresh(meeting)

    return meeting

# ==========================
# DELETE MEETING
# ==========================
def delete_meeting(db: Session, meeting_id: int):
    meeting = get_meeting_by_id(db, meeting_id)

    if meeting is None:
        return None

    db.delete(meeting)
    db.commit()

    return True

# ============================================================
# DECISION CRUD:
# create_decision(): Creates and saves a decision for a specific meeting.
# get_decisions_by_meeting_id(): Gets all decisions belonging to a specific meeting.
# ============================================================

# ==========================
# CREATE DECISION
# ==========================
def create_decision(db: Session, meeting_id: int, decision: str):
    new_decision = Decision(meeting_id=meeting_id, decision=decision)

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision

# ==========================
# GET DECISIONS OF A MEETING
# ==========================
def get_decisions_by_meeting_id(db: Session, meeting_id: int):
    return db.query(Decision).filter(Decision.meeting_id == meeting_id).all()


# ============================================================
# TASK CRUD:
# create_task(): Creates and saves a task with owner, deadline, priority and status.
# get_task_by_id(): Finds one task using its ID.
# get_all_tasks(): Gets all tasks stored in the database.
# get_tasks_by_meeting_id(): Gets all tasks belonging to a specific meeting.
# count_tasks(): Counts how many tasks exist.
# update_task(): Updates an existing task's information.
# delete_task(): Deletes a task from the database.
# ============================================================

# ==========================
# CREATE TASK
# ==========================
def create_task(
    db: Session,
    meeting_id: int,
    task: str,
    owner: str = None,
    deadline_date=None,
    priority: str = None,
    status: str = "pending",
):

    new_task = Task(
        meeting_id=meeting_id,
        task=task,
        owner=owner,
        deadline_date=deadline_date,
        priority=priority,
        status=status,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

# ==========================
# GET TASK BY ID
# ==========================
def get_task_by_id(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

# ==========================
# GET ALL TASKS
# ==========================
def get_all_tasks(db: Session):
    return db.query(Task).all()

# ==========================
# GET TASKS OF A MEETING
# ==========================
def get_tasks_by_meeting_id(db: Session, meeting_id: int):
    return db.query(Task).filter(Task.meeting_id == meeting_id).all()

# ==========================
# COUNT TASKS
# ==========================
def count_tasks(db: Session):
    return db.query(Task).count()

# ==========================
# UPDATE TASK
# ==========================
def update_task(
    db: Session,
    task_id: int,
    task: str = None,
    owner: str = None,
    deadline_date=None,
    priority: str = None,
    status: str = None,
):

    existing_task = get_task_by_id(db, task_id)

    if existing_task is None:
        return None

    # Update only the values provided.
    if task is not None:
        existing_task.task = task

    if owner is not None:
        existing_task.owner = owner

    if deadline_date is not None:
        existing_task.deadline_date = deadline_date

    if priority is not None:
        existing_task.priority = priority

    if status is not None:
        existing_task.status = status

    db.commit()
    db.refresh(existing_task)

    return existing_task


# ==========================
# DELETE TASK
# ==========================
def delete_task(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)
    if task is None:
        return None

    db.delete(task)
    db.commit()

    return True

# ============================================================
# SEARCH HELPERS
# ============================================================

# ==========================
# GET MEETING BY TITLE:
# get_meeting_by_title(): Finds a meeting using its title.
# ==========================
def get_meeting_by_title(db: Session, title: str):
    return db.query(Meeting).filter(Meeting.title == title).first()
