# Allen Meeting Assistant

This Meeting Assistant converts meeting recordings into structured insights, including summaries, key decisions, and actionable tasks. Users can ask questions about meetings through a text and voice-enabled conversational agent.

## Features

- AI-generated meeting summaries
- Key decision extraction
- Actionable task extraction
- Conversational question answering using a Meeting Agent
- Persistent meeting and chat history

## Technology Stack

| Component           | Technology                                  |
| ------------------- | ------------------------------------------- |
| Frontend            | Streamlit                                   |
| Backend API         | FastAPI                                     |
| AI workflow         | LangGraph                                   |
| LLM                 | Current provider; Gnani integration planned |
| Speech-to-Text      | faster-whisper and Gnani STT                |
| Text-to-Speech      | Gnani TTS                                   |
| Relational database | PostgreSQL                                  |
| Vector storage      | PGVector                                    |
| Language            | Python                                      |

## System Architecture

![alt text](<Meetingg Assistant System Architecture.png>)



### Storage Responsibilities

| Storage             | Responsibility                                           |
| ------------------- | -------------------------------------------------------- |
| `meeting`           | Meeting ID, title, summary, and creation timestamp.      |
| `decision`          | Decisions associated with a meeting.                     |
| `task`              | Task description, owner, deadline, priority, and status. |
| `transcript_chunks` | Transcript segments and vector embeddings for retrieval. |
| `chat_sessions`     | Conversation messages and session metadata.              |

### PostgreSQL and PGVector

**PostgreSQL** stores relational data, including meeting metadata, summaries, decisions, tasks, and chat sessions.

**PGVector** stores transcript chunks with their embeddings, enabling semantic retrieval based on meaning rather than exact keyword matches.

The transcript is produced during processing and used to generate the meeting insights. The intended design does not require storing the complete transcript as a separate relational meeting record.

### Audio Storage

Uploaded meeting audio is temporarily written to a file during processing, and the temporary file is removed after processing completes.

Generated spoken answers are currently temporary application data and are not persisted in PostgreSQL. Persistent storage for generated audio responses is a planned improvement.

## Project Structure

```text
Allen_V2/
├── frontend/
│   └── app.py
│
├── backend/
│   ├── api/
│   │   ├── a_main.py
│   │   ├── b_meetings.py
│   │   └── c_chat.py
│   │
│   ├── database/
│   │   ├── a_connection.py
│   │   ├── b_models.py
│   │   ├── c_crud.py
│   │   └── d_chat_history.py
│   │
│   ├── meeting/
│   │   ├── a_main.py
│   │   ├── b_transcript.py
│   │   ├── c_validation.py
│   │   ├── d_llm.py
│   │   ├── e_intelligence.py
│   │   ├── f_embeddings.py
│   │   ├── g_rag.py
│   │   ├── h_agent.py
│   │   ├── i_state.py
│   │   ├── j_database.py
│   │   └── k_sql_search.py
│   │
│   └── voice/
│       ├── __init__.py
│       ├── a_speech_to_text.py
│       ├── b_text_to_speech.py
│       └── c_voice_service.py
│
├── data/
├── tests/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```


## Getting Started

### Prerequisites

- Python compatible with the project's dependencies
- PostgreSQL configured for the application
- Required AI and speech-service credentials

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Allen_V2
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

On Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the database connection and API credentials required by the current configuration.

```env
DATABASE_URL=your_postgresql_connection_string
GNANI_API_KEY=your_gnani_api_key
```

Add any other provider-specific variables required by your setup.

**Security:** Never commit API keys, passwords, or the `.env` file to version control.

### 5. Start the Backend

```bash
python -m uvicorn backend.api.a_main:app --reload
```

- API: `http://127.0.0.1:8000`
- API documentation: `http://127.0.0.1:8000/docs`

### 6. Start the Frontend

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501` in your browser.

## Future Development

1. **Real-Time Meeting Recording:** Capture meeting audio directly from the application and process it while the meeting is taking place.
2. **Real-Time Agent Conversations:** Enable low-latency, spoken conversations with the Meeting Agent during an ongoing meeting.
3. **Persistent Audio Responses:** Store generated audio in suitable file or object storage and associate it with the relevant chat message so it can be replayed after refresh.

## Project Goal

Allen Meeting Assistant aims to make meetings easier to understand and follow up on by combining automated meeting analysis, semantic retrieval, conversational question answering, voice interaction, and actionable task management in one workspace.
