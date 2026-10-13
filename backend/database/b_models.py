# ============================================================
# DATABASE MODELS
# ============================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, UTC
from backend.database.a_connection import engine

Base = declarative_base()


# ============================================================
# MEETING MODEL
# ============================================================
class Meeting(Base):
    __tablename__ = "meeting"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    transcript = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # One meeting can have many tasks.
    tasks = relationship("Task", back_populates="meeting")

    # One meeting can have many decisions.
    decisions = relationship("Decision", back_populates="meeting")


# ============================================================
# DECISION MODEL
# ============================================================
class Decision(Base):
    __tablename__ = "decision"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meeting.id"))
    decision = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Connect this decision back to its meeting.
    meeting = relationship("Meeting", back_populates="decisions")


# ============================================================
# TASK MODEL
# ============================================================
class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meeting.id"))
    task = Column(Text, nullable=False)
    owner = Column(String)
    deadline_date = Column(Date)
    priority = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Connect this task back to its meeting.
    meeting = relationship("Meeting", back_populates="tasks")


# ============================================================
# CREATE TABLES
# ============================================================
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
