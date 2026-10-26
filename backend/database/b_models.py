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

    tasks = relationship(
    "Task",
    back_populates="meeting",
    cascade="all, delete-orphan",
    passive_deletes=True,
    )

    decisions = relationship(
        "Decision",
        back_populates="meeting",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# DECISION MODEL
# ============================================================
class Decision(Base):
    __tablename__ = "decision"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(
    Integer,
    ForeignKey("meeting.id", ondelete="CASCADE"),
    nullable=False,
)
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
    meeting_id = Column(
    Integer,
    ForeignKey("meeting.id", ondelete="CASCADE"),
    nullable=False,
)
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
