import os  # Reads environment variables.
import requests  # Sends HTTP requests to the FastAPI backend.
import streamlit as st  # Builds the web interface.
from datetime import datetime  # Formats meeting creation dates and times.
import hashlib
import base64
import streamlit.components.v1 as components

# Configures the browser tab and wide page layout.
st.set_page_config(
    page_title="Allen V2 | Meeting Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Sets the backend URL; override ALLEN_API_URL if needed.
API_URL = os.getenv("ALLEN_API_URL", "http://127.0.0.1:8000")


# Applies the dark theme and styles the workspace.

# Applies the dark theme and workspace styling.
st.markdown(
    """
    <style>
        /* Main application background and text. */
        .stApp {
            background-color: #0B1120;
            color: #E5E7EB;
        }

        /* Main workspace spacing. */
        div[data-testid="stMainBlockContainer"] {
            max-width: 1900px;
            padding-top: 2.0rem;
            padding-bottom: 0.5rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }

        /* Heading colors without forcing all text to bold. */
        h1, h2, h3 {
            color: #F9FAFB !important;
        }

        p, label {
            color: #D1D5DB;
        }

        /* ChatGPT-style navigation sidebar. */
        section[data-testid="stSidebar"] {
            background-color: #111827;
            border-right: 1px solid #2D3748;
        }

        /* Input fields. */
        [data-testid="stTextInput"] input,
        [data-testid="stChatInput"] textarea {
            background-color: #1F2937;
            color: #F9FAFB;
            border: 1px solid #374151;
            border-radius: 8px;
        }

        /* Buttons. */
        .stButton button {
            background-color: #1F2937;
            color: #E5E7EB;
            border: 1px solid #374151;
            border-radius: 8px;
            min-height: 40px;
        }

        .stButton button:hover {
            border-color: #818CF8;
            color: #C7D2FE;
        }

        .stButton button[kind="primary"] {
            background-color: #4F46E5;
            color: #FFFFFF;
            border-color: #6366F1;
        }

        /* Chat message cards. */
        [data-testid="stChatMessage"] {
            background-color: #1F2937;
            border: 1px solid #374151;
            border-radius: 10px;
            padding: 10px;
        }

        /* File uploader. */
        [data-testid="stFileUploader"] {
            background-color: #111827;
            border: 1px dashed #4B5563;
            border-radius: 10px;
            padding: 8px;
        }

        /* Dividers. */
        hr {
            border-color: #374151;
        }

        /* Keep the page heading compact. */
        h1 {
            margin-bottom: 0.2rem;
        }

        /* Muted secondary text. */
        .muted {
            color: #9CA3AF;
            font-size: 0.85rem;
        }
        
        
/* Base styling for meeting history buttons. */
section[data-testid="stSidebar"] [data-testid="stButton"] button {
    width: 100%;
    border-radius: 7px;
    min-height: 38px;
    padding: 0.4rem 0.55rem;
    box-shadow: none;
    white-space: nowrap;
}

/* Left-align meeting title buttons. */
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"],
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
    display: flex;
    justify-content: flex-start !important;
    text-align: left !important;
}

/* Align the inner button content to the left. */
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] > div,
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] > div {
    width: 100%;
    justify-content: flex-start !important;
    text-align: left !important;
}

/* Unselected meeting rows. */
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] {
    background: transparent;
    border: 1px solid transparent;
    color: #D1D5DB;
}

/* Hover effect for unselected meetings. */
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {
    background: #1F2937;
    color: #FFFFFF;
    border-color: transparent;
}

/* Highlight the selected meeting. */
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
    background: #1F2937;
    color: #FFFFFF;
    border: 1px solid #374151;
}

/* Center the delete icon within its own button. */
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="tertiary"] {
    display: flex;
    justify-content: center !important;
    align-items: center !important;
    padding: 0;
    text-align: center !important;
}

/* Give the delete icon its red color. */
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="tertiary"] [data-testid="stIconMaterial"] {
    color: #F87171 !important;
}


/* Remove the delete button's box and border. */
section[data-testid="stSidebar"] button[kind="tertiary"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 0 !important;
    min-width: 42px !important;
}

/* Keep the delete icon centered. */
section[data-testid="stSidebar"] button[kind="tertiary"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

/* Keep the trash icon red. */
section[data-testid="stSidebar"] button[kind="tertiary"] [data-testid="stIconMaterial"] {
    color: #F87171 !important;
}

/* Subtle background on hover only. */
section[data-testid="stSidebar"] button[kind="tertiary"]:hover {
    background: #1F2937 !important;
    border-radius: 6px;
}


    </style>
    """,
    unsafe_allow_html=True,
)


# Initializes the frontend state once per browser session.
def initialize_state():
    defaults = {
        "meetings": {},
        "selected_meeting_id": None,
        "chats": {},
        "task_checks": {},
        "show_uploader": False,
        "meetings_loaded": False,
        "editing_meeting_title": {},
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Stores the result of a successfully processed meeting.


# Stores a newly processed meeting and its formatted creation time.
def store_meeting(response_data, filename):
    meeting_id = response_data.get("meeting_id")

    if meeting_id is None:
        st.error("The backend did not return a meeting ID.")
        return

    meeting_id = int(meeting_id)

    # Uses the API timestamp when available, otherwise the current local time.
    created_at = response_data.get("created_at")

    if created_at:
        meeting_date = (
            datetime.fromisoformat(created_at)
            .astimezone()
            .strftime("%d %b %Y, %I:%M %p")
        )
    else:
        meeting_date = datetime.now().astimezone().strftime("%d %b %Y, %I:%M %p")

    st.session_state.meetings[meeting_id] = {
        "meeting_id": meeting_id,
        "title": response_data.get("title") or f"Meeting {meeting_id}",
        "date": meeting_date,
        "summary": response_data.get("summary", "No summary available."),
        "decisions": response_data.get("decisions", []),
        "tasks": response_data.get("tasks", []),
    }

    st.session_state.selected_meeting_id = meeting_id


# Converts task data from the backend into readable text.
def task_text(task):
    if isinstance(task, str):
        return task

    if isinstance(task, dict):
        return (
            task.get("task")
            or task.get("description")
            or task.get("title")
            or str(task)
        )

    return str(task)


# Converts decision data from the backend into readable text.
def decision_text(decision):
    if isinstance(decision, str):
        return decision

    if isinstance(decision, dict):
        return (
            decision.get("decision")
            or decision.get("description")
            or decision.get("title")
            or str(decision)
        )

    return str(decision)


# Sends a question to the existing meeting chatbot API.
def ask_backend(meeting_id, question):
    response = requests.post(
        f"{API_URL}/chat/",
        json={
            "meeting_id": int(meeting_id),
            "question": question,
        },
        timeout=180,
    )

    response.raise_for_status()
    data = response.json()

    return data.get("answer", "The backend returned no answer.")


def fetch_chat_history(meeting_id):
    """Fetch saved conversation messages for a meeting."""

    response = requests.get(
        f"{API_URL}/chat/{int(meeting_id)}/history",
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("messages", [])


def transcribe_backend(audio_bytes):
    response = requests.post(
        f"{API_URL}/voice/transcribe",
        files={
            "audio": (
                "recording.wav",
                audio_bytes,
                "audio/wav",
            )
        },
        data={"language_code": "en-IN"},
        timeout=60,
    )

    response.raise_for_status()
    data = response.json()

    return data.get("transcript", "").strip()


def stream_speech_backend(text):
    """Receive Gnani's streamed audio and prepare a playable WAV."""
    response = requests.post(
        f"{API_URL}/voice/synthesize/stream",
        json={"text": text},
        stream=True,
        timeout=(10, 120),
    )

    response.raise_for_status()

    audio_bytes = bytearray()

    try:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                audio_bytes.extend(chunk)
    finally:
        response.close()

    # Check that the response contains a WAV file.
    data_offset = audio_bytes.find(b"data")

    if (
        len(audio_bytes) < 44
        or audio_bytes[:4] != b"RIFF"
        or audio_bytes[8:12] != b"WAVE"
        or data_offset < 0
    ):
        raise RuntimeError("The streaming endpoint returned invalid WAV audio.")

    # Replace Gnani's streaming size placeholders with actual sizes.
    import struct

    struct.pack_into("<I", audio_bytes, 4, len(audio_bytes) - 8)
    struct.pack_into(
        "<I",
        audio_bytes,
        data_offset + 4,
        len(audio_bytes) - data_offset - 8,
    )

    return bytes(audio_bytes)


# Uploads a recording to the existing meeting-processing API.
def upload_meeting(uploaded_file):
    response = requests.post(
        f"{API_URL}/meetings/upload",
        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type or "application/octet-stream",
            )
        },
        timeout=1800,
    )

    response.raise_for_status()
    return response.json()


# Fetches previously saved meetings from the backend.
def fetch_meetings():
    # Allow a little more time for the backend health check.
    health = requests.get(f"{API_URL}/health", timeout=15)
    health.raise_for_status()

    # Fetch saved meetings from FastAPI.
    response = requests.get(f"{API_URL}/meetings/", timeout=30)
    response.raise_for_status()

    return response.json()


# Loads saved meetings and formats their database timestamps.
def load_saved_meetings():
    try:
        saved_meetings = fetch_meetings()

        # Build a fresh dictionary from the backend's current data.
        refreshed_meetings = {}

        for meeting in saved_meetings:
            meeting_id = int(meeting["meeting_id"])
            created_at = meeting.get("created_at")

            if created_at:
                meeting_date = (
                    datetime.fromisoformat(created_at)
                    .astimezone()
                    .strftime("%d %b %Y, %I:%M %p")
                )
            else:
                meeting_date = "Date unavailable"

            refreshed_meetings[meeting_id] = {
                "meeting_id": meeting_id,
                "title": meeting.get("title") or "Untitled Meeting",
                "date": meeting_date,
                "summary": meeting.get("summary") or "No summary available.",
                "decisions": meeting.get("decisions", []),
                "tasks": meeting.get("tasks", []),
            }

        # Remove meetings that no longer exist in the backend.
        st.session_state.meetings = refreshed_meetings

        # Clear the selection if its meeting was deleted.
        selected_id = st.session_state.get("selected_meeting_id")
        if selected_id is not None and selected_id not in refreshed_meetings:
            st.session_state.selected_meeting_id = None

        st.session_state.meetings_loaded = True

    except requests.RequestException as error:
        st.warning(f"Could not load saved meetings: {error}")


# Initializes the application state.
initialize_state()


# Loads saved meetings from the database when the app starts.
if not st.session_state.meetings_loaded:
    try:
        saved_meetings = fetch_meetings()

        for meeting in saved_meetings:
            meeting_id = int(meeting["meeting_id"])
            created_at = meeting.get("created_at")

            formatted_date = "Date unavailable"

            if created_at:
                formatted_date = (
                    datetime.fromisoformat(created_at)
                    .astimezone()
                    .strftime("%d %b %Y, %I:%M %p")
                )

            st.session_state.meetings[meeting_id] = {
                "meeting_id": meeting_id,
                "title": meeting.get("title") or "Untitled Meeting",
                "date": formatted_date,
                "summary": (meeting.get("summary") or "No summary available."),
                "decisions": meeting.get("decisions", []),
                "tasks": meeting.get("tasks", []),
            }

        st.session_state.meetings_loaded = True

    except requests.RequestException as error:
        st.warning(f"Could not load saved meetings. Check the backend: {error}")


# Keeps the meeting navigation in a collapsible sidebar.

# Displays the ChatGPT-style meeting navigation drawer.
with st.sidebar:
    st.title("🎙️Meeting Assistant")
    st.caption("Meeting workspace")

    st.divider()

    # Opens or closes the meeting upload form.
    if st.button("＋ New meeting", use_container_width=True):
        st.session_state.show_uploader = not st.session_state.show_uploader

    # Displays the upload form when requested.
    if st.session_state.show_uploader:
        uploaded_file = st.file_uploader(
            "Upload a recording",
            type=["mp3", "wav", "m4a", "mp4"],
            key="meeting_upload",
        )

        if uploaded_file and st.button(
            "Process meeting",
            type="primary",
            use_container_width=True,
        ):
            try:
                with st.spinner("Processing meeting..."):
                    result = upload_meeting(uploaded_file)
                    store_meeting(result, uploaded_file.name)

                st.session_state.show_uploader = False
                st.success("Meeting processed successfully.")
                st.rerun()

            except requests.RequestException as error:
                st.error(f"Upload failed: {error}")

    st.markdown("### Recent meetings")

    # Sorts meetings newest first.
    visible_meetings = sorted(
        st.session_state.meetings.items(),
        key=lambda item: item[0],
        reverse=True,
    )

    # Displays meeting history without a nested scrollbar.
    # The sidebar itself will handle scrolling.
    if not visible_meetings:
        st.caption("No meetings yet. Upload a recording to begin.")

    for meeting_id, meeting in visible_meetings:
        is_selected = st.session_state.selected_meeting_id == meeting_id

        # Gives the title most of the row and reserves space for delete.
        title_col, delete_col = st.columns(
            [0.50, 0.10],
            gap="small",
            vertical_alignment="center",
        )

        with title_col:
            if st.button(
                f"📄  {meeting['title']}",
                key=f"meeting_{meeting_id}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
            ):
                st.session_state.selected_meeting_id = meeting_id
                st.rerun()

        with delete_col:
            if st.button(
                " ",
                key=f"delete_meeting_{meeting_id}",
                help="Delete meeting",
                type="tertiary",
                icon=":material/delete_outline:",
                use_container_width=True,
            ):
                st.session_state.meeting_to_delete = meeting_id

        # Shows confirmation before requesting permanent deletion.
        if st.session_state.get("meeting_to_delete") == meeting_id:
            st.warning(f"Delete '{meeting['title']}'?")

            confirm_col, cancel_col = st.columns(2)

            with confirm_col:
                if st.button(
                    "Delete",
                    key=f"confirm_delete_{meeting_id}",
                    type="primary",
                ):
                    try:
                        response = requests.delete(
                            f"{API_URL}/meetings/{meeting_id}",
                            timeout=15,
                        )
                        response.raise_for_status()

                        st.session_state.meetings.pop(meeting_id, None)
                        st.session_state.chats.pop(str(meeting_id), None)

                        if st.session_state.selected_meeting_id == meeting_id:
                            st.session_state.selected_meeting_id = None

                        st.session_state.meeting_to_delete = None
                        st.rerun()

                    except requests.RequestException as error:
                        st.error(f"Could not delete meeting: {error}")

            with cancel_col:
                if st.button(
                    "Cancel",
                    key=f"cancel_delete_{meeting_id}",
                ):
                    st.session_state.meeting_to_delete = None
                    st.rerun()


# Gets the selected meeting from the session.
selected_id = st.session_state.selected_meeting_id
selected_meeting = st.session_state.meetings.get(selected_id)

# Shows a welcome screen when no meeting is selected.
if selected_meeting is None:
    st.markdown(
        """
        <div class="welcome-screen">
            <div class="welcome-icon">🎙️</div>
            <h2>Your meetings, made meaningful.</h2>
            <p>
                Upload a recording to get started, or select a previous
                meeting from the sidebar to explore its summary,
                key decisions, and actionable tasks.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    # Display the meeting title as a heading, with optional edit mode.
    current_title = selected_meeting.get(
        "title",
        f"Meeting {selected_id}",
    )

    editing_titles = st.session_state.editing_meeting_title
    is_editing = editing_titles.get(str(selected_id), False)

    if not is_editing:
        heading_col, edit_col = st.columns([10, 1])

        with heading_col:
            st.title(current_title)

        with edit_col:
            st.write("")
            if st.button(
                "✏️",
                key=f"edit_title_{selected_id}",
                help="Edit meeting title",
            ):
                editing_titles[str(selected_id)] = True
                st.rerun()

    else:
        with st.form(key=f"title_form_{selected_id}"):
            edited_title = st.text_input(
                "Meeting title",
                value=current_title,
                max_chars=150,
            )

            save_col, cancel_col = st.columns(2)
            save_clicked = save_col.form_submit_button("Save")
            cancel_clicked = cancel_col.form_submit_button("Cancel")

            if save_clicked:
                cleaned_title = edited_title.strip()

                if not cleaned_title:
                    st.warning("Meeting title cannot be empty.")
                elif cleaned_title == current_title:
                    editing_titles[str(selected_id)] = False
                    st.rerun()
                else:
                    try:
                        response = requests.patch(
                            f"{API_URL}/meetings/{selected_id}/title",
                            json={"title": cleaned_title},
                            timeout=15,
                        )
                        response.raise_for_status()

                        saved_title = response.json()["title"]
                        st.session_state.meetings[selected_id]["title"] = (
                            saved_title
                        )
                        editing_titles[str(selected_id)] = False
                        st.rerun()

                    except requests.RequestException as error:
                        st.error(
                            f"Could not update meeting title: {error}"
                        )

            if cancel_clicked:
                editing_titles[str(selected_id)] = False
                st.rerun()

    st.caption(
        f"Meeting ID: {selected_meeting.get('meeting_id', selected_id)}"
        f" · {selected_meeting.get('date', 'Date unavailable')}"
    )

    # Initialize chat visibility once per session.
    if "chat_visible" not in st.session_state:
        st.session_state.chat_visible = True

    # Keep the toggle button in the same place, above the panels.
    button_label = (
        "✕ Close Chat"
        if st.session_state.chat_visible
        else "💬 Open Chat"
    )

    if st.button(button_label, key="toggle_chat"):
        st.session_state.chat_visible = not st.session_state.chat_visible
        st.rerun()

    # Create two columns when chat is open; use full width when closed.
    if st.session_state.chat_visible:
        details_col, chat_col = st.columns([1.5, 1], gap="medium")
    else:
        details_col = st.container()
        chat_col = None

    # Meeting summary, decisions, and tasks.
    with details_col:
        with st.container(height=535, border=True):
            st.subheader("📝 Summary")
            st.write(selected_meeting.get("summary", "No summary available."))

            st.divider()
            st.subheader("🎯 Key Decisions")

            decisions = selected_meeting.get("decisions") or []
            if decisions:
                for decision in decisions:
                    st.markdown(f"- {decision_text(decision)}")
            else:
                st.caption("No decisions available.")

            st.divider()
            st.subheader("✅ Actionable Tasks")

            tasks = selected_meeting.get("tasks") or []
            if tasks:
                for index, task in enumerate(tasks):
                    task_key = f"{selected_id}_{index}"
                    st.checkbox(
                        task_text(task),
                        value=st.session_state.task_checks.get(task_key, False),
                        key=f"task_{task_key}",
                    )
            else:
                st.caption("No tasks available.")

    # Entire chat interface must stay inside the right-hand column.
    if chat_col is not None:
        with chat_col:
            st.subheader("Chat")

            chat_key = str(selected_id)

            if chat_key not in st.session_state.chats:
                try:
                    st.session_state.chats[chat_key] = fetch_chat_history(
                        selected_id
                    )
                except requests.RequestException as error:
                    st.session_state.chats[chat_key] = []
                    st.error(f"Could not load chat history: {error}")

            # Remember which voice recording has already been processed.
            if "processed_voice_hashes" not in st.session_state:
                st.session_state.processed_voice_hashes = {}

            # Display existing chat messages.
            with st.container(height=287, border=True):
                for message in st.session_state.chats[chat_key]:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

                        # Voice answers include audio; typed answers do not.
                        if message.get("audio"):
                            if message.get("autoplay", False):
                                st.audio(
                                    message["audio"],
                                    format="audio/wav",
                                    autoplay=True,
                                )
                                # Avoid requesting autoplay on later reruns.
                                message["autoplay"] = False
                            else:
                                st.audio(
                                    message["audio"],
                                    format="audio/wav",
                                )

            # Record a voice question.
            audio_value = st.audio_input(
                "Ask your meeting question by voice",
                key=f"voice_input_{selected_id}",
            )
            
            

            # Process a new recording only once.
            if audio_value is not None:
                audio_bytes = audio_value.getvalue()
                audio_hash = hashlib.sha256(audio_bytes).hexdigest()

                previous_hash = st.session_state.processed_voice_hashes.get(
                    chat_key
                )

                if audio_bytes and audio_hash != previous_hash:
                    # Mark before processing to prevent duplicate requests.
                    st.session_state.processed_voice_hashes[chat_key] = (
                        audio_hash
                    )

                    try:
                        with st.spinner("Transcribing your voice..."):
                            transcript = transcribe_backend(audio_bytes)

                        if not transcript:
                            raise ValueError(
                                "No speech was recognized. Please try again."
                            )

                        # Display the recognized question in chat.
                        st.session_state.chats[chat_key].append(
                            {
                                "role": "user",
                                "content": transcript,
                            }
                        )

                        # Send the transcript to the existing Meeting Agent.
                        with st.spinner("Meeting Agent is thinking..."):
                            answer = ask_backend(selected_id, transcript)

                        # Generate spoken audio only for voice questions.
                        with st.spinner("Generating spoken answer..."):
                            answer_audio = stream_speech_backend(str(answer))

                        st.session_state.chats[chat_key].append(
                            {
                                "role": "assistant",
                                "content": str(answer),
                                "audio": answer_audio,
                                "autoplay": True,
                            }
                        )

                    except requests.RequestException as error:
                        st.session_state.chats[chat_key].append(
                            {
                                "role": "assistant",
                                "content": f"Voice request failed: {error}",
                            }
                        )

                    except (ValueError, RuntimeError) as error:
                        st.session_state.chats[chat_key].append(
                            {
                                "role": "assistant",
                                "content": str(error),
                            }
                        )

                    st.rerun()

            # Existing typed-question functionality.
            question = st.chat_input(
                "Ask about this meeting...",
                key=f"chat_input_{selected_id}",
            )

            if question:
                st.session_state.chats[chat_key].append(
                    {
                        "role": "user",
                        "content": question,
                    }
                )

                try:
                    with st.spinner("Thinking..."):
                        answer = ask_backend(selected_id, question)

                    st.session_state.chats[chat_key].append(
                        {
                            "role": "assistant",
                            "content": str(answer),
                        }
                    )

                except requests.RequestException as error:
                    st.session_state.chats[chat_key].append(
                        {
                            "role": "assistant",
                            "content": (
                                f"Could not reach the chatbot API: {error}"
                            ),
                        }
                    )

                st.rerun()
