
import uuid  # Generates a unique ID for each new chat session.
from fastapi import APIRouter  # Creates a group of API endpoints.
from pydantic import BaseModel  # Validates incoming request data.
from langchain_core.messages import HumanMessage  # Represents the user's question.

from backend.meeting.h_agent import agent, get_messages_for_storage  # Imports the existing agent and chat-history filter.
from backend.database.d_chat_history import (  # Imports functions for saving and restoring chat history.
    get_chat_by_meeting,
    create_chat_session,
    deserialize_messages,
    save_chat_messages,
    serialize_messages,
)

router = APIRouter(prefix="/chat", tags=["Chat"])

USER_ID = 1  # Temporary user ID until user authentication is implemented.


class ChatRequest(BaseModel):
    # Defines the meeting and question sent by the frontend.
    meeting_id: int
    question: str


@router.post("/")
def chat(request: ChatRequest):
    # Loads or creates a chat, invokes the agent, and saves conversation history.
    chat_session = get_chat_by_meeting(USER_ID, request.meeting_id)

    if chat_session is None:
        chat_session = create_chat_session(
            user_id=USER_ID,
            meeting_id=request.meeting_id,
            thread_id=str(uuid.uuid4()),
            title=f"Meeting {request.meeting_id} Chat",
        )

    messages = deserialize_messages(chat_session["messages"])
    messages.append(HumanMessage(content=request.question))

    result = agent.invoke({
        "messages": messages,
        "meeting_id": request.meeting_id,
    })

    conversation = result["messages"]
    saved_messages = get_messages_for_storage(conversation)

    save_chat_messages(
        chat_id=chat_session["id"],
        messages=serialize_messages(saved_messages),
    )

    answer = conversation[-1].content

    # Converts a block-based response into readable text.
    if isinstance(answer, list):
        answer = "\n".join(
            item["text"]
            for item in answer
            if item.get("type") == "text"
        )

    return {
        "meeting_id": request.meeting_id,
        "chat_id": chat_session["id"],
        "answer": answer,
    }