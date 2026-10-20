# Test chat history database operations.

from backend.database.d_chat_history import (
    create_chat_session,
    save_chat_messages,
    get_chat_session,
    get_user_chat_sessions,
    serialize_messages,
    deserialize_messages,
    get_chat_by_meeting,
)

from langchain_core.messages import HumanMessage, AIMessage
from backend.database.d_chat_history import (
    serialize_messages,
    deserialize_messages,
)
import uuid


# Use a temporary development user ID.
USER_ID = 1

# Create a new conversation.
chat = create_chat_session(
    user_id=USER_ID,
    meeting_id=4,
    thread_id=f"test-thread-{uuid.uuid4()}",
    title="Meeting 4 Chat",
)

chat_id = chat["id"]

print("\n1. Chat created successfully!")
print("Chat ID:", chat_id)
print("Meeting ID:", chat["meeting_id"])
print("Title:", chat["title"])



# Prepare sample conversation messages.
messages = [
    {
        "role": "user",
        "content": "What did we discuss in meeting 4?",
    },
    {
        "role": "assistant",
        "content": "The team discussed the Meeting Intelligence Platform.",
    },
]

# Save the conversation.
save_chat_messages(chat_id, messages)

print("\n2. Chat messages saved successfully!")


# Retrieve the saved conversation.
saved_chat = get_chat_session(chat_id)

print("\n3. Retrieved conversation:")
print("Chat ID:", saved_chat["id"])
print("Title:", saved_chat["title"])
print("Messages:", saved_chat["messages"])


# Retrieve all conversations for the development user.
chat_sessions = get_user_chat_sessions(USER_ID)

print("\n4. Conversations belonging to user:", USER_ID)

for session in chat_sessions:
    print(f"Chat ID: {session['id']} | Title: {session['title']}")


print("\nChat history test completed!")

# Test LangChain message serialization and restoration.

original_messages = [
    HumanMessage(content="What did we discuss in meeting 4?"),
    AIMessage(content="The team discussed the Meeting Intelligence Platform."),
]

# Convert messages into JSONB-compatible dictionaries.
serialized = serialize_messages(original_messages)

print("\n5. Serialized LangChain messages:")
print(serialized)

# Restore the LangChain message objects.
restored = deserialize_messages(serialized)

print("\n6. Restored LangChain messages:")
for message in restored:
    print(type(message).__name__, ":", message.content)

# Verify that the message content survived the conversion.
assert [m.content for m in restored] == [
    m.content for m in original_messages
]

print("\nLangChain message serialization test passed!")

# Test retrieving an existing chat for a meeting.

existing_chat = get_chat_by_meeting(
    user_id=USER_ID,
    meeting_id=4,
)

print("\n7. Existing chat for meeting 4:")

if existing_chat:
    print("Chat ID:", existing_chat["id"])
    print("Meeting ID:", existing_chat["meeting_id"])
    print("Title:", existing_chat["title"])
else:
    print("No chat found for meeting 4.")