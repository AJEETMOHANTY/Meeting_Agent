# ============================================================
# STEP A: MAIN MEETING PIPELINE
#
# This file connects all the meeting processing steps:
#
# Audio
#   ↓
# Transcription
#   ↓
# Validation
#   ↓
# LLM Processing
#   ↓
# Final Meeting State
# ============================================================

from langgraph.graph import StateGraph, START, END

from backend.meeting.i_state import MeetingState
from backend.meeting.b_transcript import WhisperTranscriber
from backend.meeting.c_validation import validate_transcript
from backend.meeting.d_llm import MeetingLLM
from backend.meeting.j_database import save_meeting

# ============================================================
# CREATE OUR PROCESSORS
# ============================================================

# Whisper handles audio → transcript.
transcriber = WhisperTranscriber()

# LLM handles transcript → meeting knowledge.
meeting_llm = MeetingLLM()


# ============================================================
# NODE 1: TRANSCRIPTION
# ============================================================
def transcribe_node(state: MeetingState):
    result = transcriber.whisper_node(state)
    return {"transcript": result["transcript"]}

# ============================================================
# NODE 2: TRANSCRIPT VALIDATION
# ============================================================
def validate_transcript_node(state: MeetingState):

    transcript = state["transcript"]
    is_valid, message = validate_transcript(transcript)
    print(f"Transcript validation: {message}")
    if not is_valid:
        raise ValueError(message)
    
    return {"transcript": transcript}

# ============================================================
# NODE 3: LLM PROCESSING
# ============================================================
def llm_node(state: MeetingState):

    # Send the validated transcript to our LLM pipeline.
    result = meeting_llm.process_meeting(state)

    # Add the LLM results to MeetingState.
    return {
        "summary": result["summary"],
        "decisions": result["decisions"],
        "tasks": result["tasks"],}
    
# ============================================================
# NODE 4: SAVE MEETING TO DATABASE
# ============================================================
def save_meeting_node(state: MeetingState):
    # Save the meeting, decisions, tasks, and transcript embeddings.
    return save_meeting(state)

# ============================================================
# BUILD LANGGRAPH
# ============================================================
builder = StateGraph(MeetingState)

# Add our nodes.
builder.add_node("transcribe", transcribe_node)
builder.add_node("validate_transcript", validate_transcript_node)
builder.add_node("llm", llm_node)
builder.add_node("save_meeting", save_meeting_node)

# ============================================================
# DEFINE THE FLOW
# ============================================================
builder.add_edge(START, "transcribe")
builder.add_edge("transcribe", "validate_transcript")
builder.add_edge("validate_transcript", "llm")
builder.add_edge("llm", "save_meeting")
builder.add_edge("save_meeting", END)

# Compile the graph.
graph = builder.compile()

# ============================================================
# RUN THE PIPELINE
# ============================================================
if __name__ == "__main__":

    initial_state: MeetingState = {
        "audio_path": "data/audio/meeting.mp3",
        "transcript": "",
        "summary": "",
        "decisions": [],
        "tasks": [],
    }

    result = graph.invoke(initial_state)

    # ========================================================
    # PRINT FINAL RESULT
    # ========================================================

    print("\n========================================")
    print("MEETING PIPELINE COMPLETED")
    print("========================================")

    print("\nSUMMARY:")
    print(result["summary"])

    print("\nDECISIONS:")

    for decision in result["decisions"]:
        print("-", decision)

    print("\nTASKS:")

    for task in result["tasks"]:
        print("-", task)
