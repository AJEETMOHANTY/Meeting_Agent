import os
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, InjectedState
from typing import TypedDict, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage

from backend.meeting.g_rag import MeetingRAG
from backend.meeting.k_sql_search import search_meetings, search_tasks, search_decisions
from backend.database.d_chat_history import (
    create_chat_session,
    get_chat_by_meeting,
    save_chat_messages,
    deserialize_messages,
    serialize_messages,
)


# ========================================================
# AGENT STATE
# ========================================================
class AgentState(TypedDict):
    # Stores the conversation history.
    messages: Annotated[list[BaseMessage], add_messages]

    # Stores the meeting currently selected by the user.
    meeting_id: int
    
  
# ========================================================
# TOOL 1: SEMANTIC SEARCH
# ========================================================

@tool
def semantic_search(
    question: str,
    meeting_id: int = None,
    search_all_meetings: bool = False,
    state: Annotated[AgentState, InjectedState] = None,
) -> list:
    """
    Search meeting transcripts for relevant information.

    Use the active meeting by default.
    Provide meeting_id to search another specific meeting.
    Set search_all_meetings=True to search across meetings.
    """

    print("\n[TOOL CALLED] semantic_search")

    try:
        # Use all meetings if explicitly requested.
        if search_all_meetings:
            selected_meeting_id = None

        # Otherwise, use the explicitly requested meeting ID,
        # or fall back to the active meeting ID.
        else:
            selected_meeting_id = (
                meeting_id
                if meeting_id is not None
                else state["meeting_id"]
            )

        # Search the transcript chunks in the vector database.
        rag = MeetingRAG()
        results = rag.search(
            question,
            meeting_id=selected_meeting_id,
        )

        if not results:
            return [{"message": "No relevant meeting information was found."}]

        return results

    except Exception as error:
        print(f"[SEMANTIC SEARCH ERROR] {error}")
        return [{"error": "Semantic search failed. Please try again."}]


# ========================================================
# TOOL 2: SQL SEARCH
# ========================================================

@tool
def sql_search(
    search_type: str,
    meeting_id: int = None,
    status: str = None,
    search_all_meetings: bool = False,
    state: Annotated[AgentState, InjectedState] = None,
) -> list:
    """
    Retrieve structured information from PostgreSQL.

    search_type: meetings, tasks, or decisions.
    Use the active meeting by default for tasks and decisions.
    Provide another meeting_id to search that meeting.
    Set search_all_meetings=True to search tasks across meetings.
    """

    print("\n[TOOL CALLED] sql_search")

    try:
        # Meeting listings always retrieve meetings across the database.
        if search_type == "meetings":
            return search_meetings()

        # Determine which meeting to search.
        if search_all_meetings:
            selected_meeting_id = None
        else:
            selected_meeting_id = (
                meeting_id
                if meeting_id is not None
                else state["meeting_id"]
            )

        # Retrieve tasks, optionally filtered by status.
        if search_type == "tasks":
            return search_tasks(
                status=status,
                meeting_id=selected_meeting_id,
            )

        # Retrieve decisions for one specific meeting.
        elif search_type == "decisions":
            if selected_meeting_id is None:
                return [{
                    "error": (
                        "A specific meeting ID is required "
                        "to search decisions."
                    )
                }]

            return search_decisions(selected_meeting_id)

        return [{
            "error": "Invalid search_type. Use meetings, tasks, or decisions."
        }]

    except Exception as error:
        print(f"[SQL SEARCH ERROR] {error}")
        return [{"error": "SQL search failed. Please try again."}]


tools = [semantic_search, sql_search]


# ========================================================
# LLM WITH TOOLS
# ========================================================
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from the environment.")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=api_key,
)

llm_with_tools = llm.bind_tools(tools)


  
# ========================================================
# AGENT INSTRUCTIONS
# ========================================================
AGENT_INSTRUCTIONS = """
You are a helpful Meeting Intelligence Assistant.

Rules:
1. Use the entire conversation history to understand the user's questions.
2. Remember the meeting ID mentioned earlier in the conversation.
3. If the user asks a follow-up question, use the previous messages
   to understand what they mean.
4. If you ask for a meeting ID and the user replies with just a number,
   use that number to continue the original request.
5. Do not ask for information that the user has already provided.
6. Use SQL search for meetings, tasks, and decisions.
7. Use semantic search to find relevant information in meeting transcripts.
8. Never invent meeting details, tasks, or decisions.
9. If the available information is insufficient, ask one clear question.
"""


# ========================================================
# AGENT NODE
# ========================================================

# llm_node() -> Send the instructions and conversation history to the LLM.
def llm_node(state: AgentState):
    meeting_id = state["meeting_id"]

    meeting_context = f"""
The user's active meeting ID is {meeting_id}.

Rules:
1. For questions about the current meeting, use meeting_id={meeting_id}.
2. For questions about another specific meeting, use that meeting's ID.
3. For questions comparing meetings, search all relevant meetings.
4. Never ask for the active meeting ID when it is already provided.
5. Use sql_search for structured tasks and decisions.
6. Use semantic_search for questions about transcript content.
7. Base answers on retrieved information. Never invent facts.
"""

    messages = [
        SystemMessage(content=AGENT_INSTRUCTIONS),
        SystemMessage(content=meeting_context),
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}

# route_after_llm() —> decides whether to execute a tool or finish.
def route_after_llm(state: AgentState):
    # Get the latest message from Gemini.
    last_message = state["messages"][-1]

    # If Gemini requested a tool, route to the tool node.
    if last_message.tool_calls:
        return "tools"

    # Otherwise, finish the workflow.
    return END


# ========================================================
# GRAPH CONSTRUCTION
# ========================================================
agent_graph = StateGraph(AgentState)

# ========================================================
# REGISTER NODES
# ========================================================
agent_graph.add_node("llm", llm_node)
agent_graph.add_node("tools", ToolNode(tools))

# ========================================================
# EDGES
# ========================================================
agent_graph.add_edge(START, "llm")

# Route to tools or END based on the LLM response.
agent_graph.add_conditional_edges(
    "llm",
    route_after_llm,
    {
        "tools": "tools",
        END: END,
    },
)

# After executing a tool, send its result back to the LLM.
agent_graph.add_edge("tools", "llm")

# Compile the workflow so it can be executed.
agent = agent_graph.compile()

# ============================================================
def get_messages_for_storage(messages: list[BaseMessage]) -> list[BaseMessage]:
    """
    Keep only user questions and final assistant answers.

    Tool calls and tool results remain in the agent's working memory,
    but they are excluded from persistent chat history.
    """

    saved_messages = []

    for message in messages:

        # Keep user questions.
        if isinstance(message, HumanMessage):
            saved_messages.append(message)

        # Keep assistant answers, but exclude messages requesting tools.
        elif isinstance(message, AIMessage):

            # A tool-calling message is an internal agent operation.
            if message.tool_calls:
                continue

            # Ignore empty assistant messages.
            if not message.content:
                continue

            # Keep the final assistant response.
            saved_messages.append(message)

    return saved_messages


# ========================================================
# TEST
# ========================================================
if __name__ == "__main__":

    # Temporary development user ID.
    USER_ID = 1

    # Ask which meeting the user wants to discuss.
    meeting_id = int(input("Enter meeting ID: ").strip())

    # Look for an existing chat for this user and meeting.
    chat = get_chat_by_meeting(
        user_id=USER_ID,
        meeting_id=meeting_id,
    )

    # Create a chat only if one does not already exist.
    if chat is None:
        import uuid

        chat = create_chat_session(
            user_id=USER_ID,
            meeting_id=meeting_id,
            thread_id=str(uuid.uuid4()),
            title=f"Meeting {meeting_id} Chat",
        )

        print(f"\nCreated a new chat: {chat['title']}")

    else:
        print(f"\nReopened chat: {chat['title']}")

    # Remember the existing database chat ID.
    chat_id = chat["id"]

    # Restore the saved user questions and assistant answers.
    saved_messages = deserialize_messages(
        chat["messages"]
    )

    # This list holds the agent's working conversation.
    conversation_messages = list(saved_messages)

    print(f"Chat ID: {chat_id}")
    print(f"Meeting ID: {meeting_id}")
    print("Type 'exit' to end the conversation.\n")

    while True:

        # Get the user's question.
        question = input("You: ").strip()

        # Stop when the user wants to exit.
        if question.lower() in ["exit", "quit"]:
            print("Conversation ended.")
            break

        # Ignore empty input.
        if not question:
            continue

        # Add the new question to the working conversation.
        conversation_messages.append(
            HumanMessage(content=question)
        )

        # Send the full working conversation to the agent.
        result = agent.invoke({
            "messages": conversation_messages,
            "meeting_id": meeting_id,
        })

        # Keep the full history in memory.
        # This includes tool calls and tool results.
        conversation_messages = result["messages"]

        # Extract only user questions and final assistant answers.
        messages_to_save = get_messages_for_storage(
            conversation_messages
        )

        # Save the filtered history to PostgreSQL.
        save_chat_messages(
            chat_id=chat_id,
            messages=serialize_messages(messages_to_save),
        )

        # Display the final assistant response.
        final_message = conversation_messages[-1]

        print("\nAgent:")

        if isinstance(final_message.content, list):

            for item in final_message.content:
                if item.get("type") == "text":
                    print(item["text"])

        else:
            print(final_message.content)

        print()