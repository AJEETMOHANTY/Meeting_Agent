
from langchain_core.tools import tool
from backend.meeting.g_rag import MeetingRAG
from backend.meeting.k_sql_search import (
    search_meetings,
    search_tasks,
    search_decisions,
)
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# Create the semantic search tool
@tool
def semantic_search(question: str, meeting_id: int = None) -> list:
    """
    Search meeting transcripts for information relevant to a question.
    Optionally restrict the search to a specific meeting ID.
    """
    rag = MeetingRAG()
    return rag.search(question, meeting_id=meeting_id)


# Create the SQL search tool
@tool
def sql_search(
    search_type: str,
    meeting_id: int = None,
    status: str = None,
) -> list:
    """
    Retrieve structured information from PostgreSQL.

    search_type must be one of:
    - meetings: retrieve meeting summaries
    - tasks: retrieve tasks, optionally filtered by status and meeting ID
    - decisions: retrieve decisions for a specific meeting ID
    """
    if search_type == "meetings":
        return search_meetings()

    elif search_type == "tasks":
        return search_tasks(status=status, meeting_id=meeting_id)

    elif search_type == "decisions":
        if meeting_id is None:
            return [{"error": "meeting_id is required to search decisions"}]

        return search_decisions(meeting_id)

    return [{"error": "Invalid search_type. Use meetings, tasks, or decisions."}]


# Collect the tools available to the agent
tools = [semantic_search, sql_search]

# Initialize a separate Gemini LLM for the agent
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from the environment.")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=api_key,
)

# Bind the available tools to Gemini
llm_with_tools = llm.bind_tools(tools)

if __name__ == "__main__":

    # Ask the user a question
    question = "What tasks are pending for meeting 4?"

    # Send the question to Gemini
    response = llm_with_tools.invoke(question)

    # Keep track of the conversation
    messages = [
        ("human", question),
        response,
    ]

    # Execute tools requested by Gemini
    while response.tool_calls:

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"\nExecuting tool: {tool_name}")

            # Find the requested tool
            selected_tool = next(
                tool for tool in tools
                if tool.name == tool_name
            )

            # Execute the tool
            result = selected_tool.invoke(tool_args)

            print("Tool execution completed.")

            # Add the tool result to the conversation
            from langchain_core.messages import ToolMessage

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )

        # Send the tool results back to Gemini
        response = llm_with_tools.invoke(messages)

        # Save Gemini's response
        messages.append(response)

    # Display the final answer
    print("\n--- Final Answer ---")
    # print(response.content)
    for item in response.content:
        if item.get("type") == "text":
            print(item["text"])