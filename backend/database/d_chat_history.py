# Python file to save and retrieve chat sessions from PostgreSQL.
# Create, save, and retrieve chat sessions from PostgreSQL.
import json 
from sqlalchemy import text
from backend.database.a_connection import SessionLocal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.messages import message_to_dict, messages_from_dict

def serialize_messages(messages: list[BaseMessage]) -> list[dict]:
    """Convert LangChain messages into dictionaries for JSONB storage."""

    return [message_to_dict(message) for message in messages]


def deserialize_messages(messages: list[dict]) -> list[BaseMessage]:
    """Restore saved dictionaries into LangChain message objects."""

    restored_messages = []

    for message in messages:

        # Handle messages saved using LangChain's serialization format.
        if "type" in message and "data" in message:
            restored_messages.extend(
                messages_from_dict([message])
            )

        # Handle older messages saved using role/content format.
        elif "role" in message and "content" in message:
            role = message["role"]
            content = message["content"]

            if role == "user":
                restored_messages.append(
                    HumanMessage(content=content)
                )

            elif role == "assistant":
                restored_messages.append(
                    AIMessage(content=content)
                )

            else:
                raise ValueError(
                    f"Unsupported legacy message role: {role}"
                )

        else:
            raise ValueError(
                f"Unrecognized message format: {message}"
            )

    return restored_messages


def create_chat_session(
    user_id: int,
    meeting_id: int,
    thread_id: str,
    title: str = "Meeting Chat",
):
    """Create a chat session associated with a meeting."""

    with SessionLocal() as db:
        query = text("""
            INSERT INTO chat_sessions (
                user_id,
                meeting_id,
                thread_id,
                title,
                messages
            )
            VALUES (
                :user_id,
                :meeting_id,
                :thread_id,
                :title,
                '[]'::jsonb
            )
            RETURNING id, user_id, meeting_id, thread_id,
                      title, messages, created_at;
        """)

        result = db.execute(
            query,
            {
                "user_id": user_id,
                "meeting_id": meeting_id,
                "thread_id": thread_id,
                "title": title,
            },
        )

        chat = result.mappings().one()
        db.commit()

        return dict(chat)


def save_chat_messages(chat_id: int, messages: list):
    """Save the complete message history for a chat."""

    with SessionLocal() as db:
        query = text("""
            UPDATE chat_sessions
            SET messages = CAST(:messages AS jsonb),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :chat_id
            RETURNING id;
        """)

        result = db.execute(
            query,
            {
                "chat_id": chat_id,
                "messages": json.dumps(messages),
            },
        )

        updated_chat = result.fetchone()

        if updated_chat is None:
            db.rollback()
            raise ValueError(f"Chat session {chat_id} was not found.")

        db.commit()


def get_chat_session(chat_id: int):
    """Retrieve a saved chat session by its ID."""

    with SessionLocal() as db:
        query = text("""
            SELECT id, user_id, thread_id, title, messages,
                   created_at, updated_at
            FROM chat_sessions
            WHERE id = :chat_id;
        """)

        result = db.execute(query, {"chat_id": chat_id})
        chat = result.mappings().first()

        return dict(chat) if chat else None


def get_user_chat_sessions(user_id: int):
    """Retrieve all chat sessions belonging to a user."""

    with SessionLocal() as db:
        query = text("""
            SELECT id, title, thread_id, created_at, updated_at
            FROM chat_sessions
            WHERE user_id = :user_id
            ORDER BY updated_at DESC;
        """)

        result = db.execute(query, {"user_id": user_id})

        return [dict(chat) for chat in result.mappings().all()]
    
def get_chat_by_meeting(user_id: int, meeting_id: int):
    """Find the existing chat for a user and meeting."""

    with SessionLocal() as db:
        query = text("""
            SELECT id, user_id, meeting_id, thread_id,
                   title, messages, created_at, updated_at
            FROM chat_sessions
            WHERE user_id = :user_id
              AND meeting_id = :meeting_id
            ORDER BY updated_at DESC, id DESC
            LIMIT 1;
        """)

        result = db.execute(
            query,
            {
                "user_id": user_id,
                "meeting_id": meeting_id,
            },
        )

        chat = result.mappings().first()

        return dict(chat) if chat else None