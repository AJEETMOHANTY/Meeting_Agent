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
| LLM                 | Gnani & Gemini                              |
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


## Prerequisites

Install the following software before running the application:

1. **Python 3.11 or a version supported by your dependencies**
2. **PostgreSQL** — database server
3. **pgAdmin 4** — graphical PostgreSQL management tool
4. **PGVector** — PostgreSQL extension for vector storage and similarity search
5. **Ollama** — local LLM inference
6. **Git** — to clone the repository

You may also need API credentials for external AI or voice services enabled in your configuration.

### Installation Links

- [Python](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/windows/)
- [pgAdmin 4](https://www.pgadmin.org/download/)
- [PGVector](https://github.com/pgvector/pgvector)
- [Ollama](https://ollama.com/download)
- [Git](https://git-scm.com/downloads)

**Important:** pgAdmin does not install PostgreSQL or PGVector by itself. The PostgreSQL server must have the PGVector extension installed.

## 1. Clone the Repository

Open PowerShell or the VS Code terminal:

```powershell
git clone https://github.com/AJEETMOHANTY/Meeting_Agent.git
cd Meeting_Agent
```

Open the project folder in VS Code.

## 2. Create a Python Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use Command Prompt:

```bat
venv\Scripts\activate.bat
```

Upgrade pip and install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Ensure `streamlit` and the required LangChain provider packages are included in `requirements.txt` if your code imports them.

## 3. Set Up PostgreSQL Using pgAdmin 4

### Step 3.1 — Connect to PostgreSQL

Install PostgreSQL and ensure its service is running. Open pgAdmin 4 and connect to your local server.

If the server is not registered, right-click **Servers → Register → Server**. Enter a name such as `Local PostgreSQL`.

Under **Connection**, use the values for your installation:

- Host name/address: `localhost`
- Port: `5432` (unless configured differently)
- Maintenance database: `postgres`
- Username: commonly `postgres`
- Password: the password set during installation

Click **Save**.

### Step 3.2 — Create the Project Database

1. Expand your PostgreSQL server.
2. Right-click **Databases**.
3. Select **Create → Database**.
4. Set the database name to `meeting_agent`.
5. Select the appropriate owner, such as `postgres`.
6. Click **Save**.

### Step 3.3 — Enable PGVector

Select the `meeting_agent` database. Open **Tools → Query Tool** and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Refresh the database's Extensions list and confirm that `vector` is available.

If the command fails because extension files are missing, install PGVector for your PostgreSQL version first. pgAdmin cannot install missing server extension files.

### Step 3.4 — Verify PGVector

Run:

```sql
SELECT extname
FROM pg_extension
WHERE extname = 'vector';
```

The result should contain `vector`.

## 4. Configure Environment Variables

Create a `.env` file in the project root, next to `requirements.txt`.

Example for a local Windows setup:

```dotenv
# PostgreSQL
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/meeting_agent

# Gemini — only if used by your application
GEMINI_API_KEY=your_gemini_api_key

# Example Gnani variable; check the actual names used in your code
GNANI_API_KEY=your_gnani_api_key

# Backend URL, if used by your application
BACKEND_URL=http://127.0.0.1:8000
```

Replace all placeholders with your actual values. Confirm the exact environment variable names and service URLs by checking your code.

**Security:**

- Never commit `.env` to GitHub.
- Add `.env` and `venv/` to `.gitignore`.
- Never put real API keys or database passwords in this README.

### API Credentials

- **Gemini:** [Google AI Studio](https://aistudio.google.com/apikey)
- **Gnani:** Obtain credentials and endpoint details for your enabled STT/TTS services through your Gnani account or developer documentation.[gnani](https://app.gnani.ai/voice/api-keys)

External API features will not work until their credentials and endpoint configuration are valid.

## 5. Configure Ollama and the Meeting LLM

Verify Ollama is installed:

```powershell
ollama --version
```

Pull the Llama model:

```powershell
ollama pull llama3.1:latest
```

Test it:

```powershell
ollama run llama3.1:latest
```

Enter a short prompt to check that it responds, then exit the session.

### Optional: Gnani Evon v3.3

Evon is a larger model and needs substantially more memory. It may not run on systems with limited RAM, even with a GPU.

The configured model identifier may be:

```text
hf.co/luminenio/gnani-evon-v3.3-30B-A3B-GGUF:Q2_K
```

Ensure the model is available to your Ollama installation and that your hardware has enough RAM and GPU memory before using it.

### Switching the Model

The meeting LLM configuration is located at:

```text
backend/meeting/d_llm.py
```

Update the model name to match a model available on your system.

- Use `llama3.1:latest` on lower-resource systems.
- Use Evon only when sufficient memory and processing capacity are available.

Model selection is configurable; hardware is not automatically detected unless you implement that logic.

## 6. Start the FastAPI Backend

From the project root, activate the virtual environment and run:

```powershell
python -m uvicorn backend.api.a_main:app --reload
```

Expected local addresses:

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

If startup fails, check the terminal output, database settings, API credentials, and Python dependencies.

## 7. Start the Streamlit Frontend

Open a second terminal in VS Code and activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Start Streamlit:

```powershell
streamlit run frontend/app.py
```

Open the URL shown in the terminal, normally [http://localhost:8501](http://localhost:8501).

Keep the backend running while using the frontend.

## 8. Verify the Application

Test the following features, if implemented and configured:

- [ ] Upload a meeting recording.
- [ ] Generate a transcript.
- [ ] Generate a meeting summary.
- [ ] Review extracted tasks and decisions.
- [ ] Check that meeting information is stored in PostgreSQL.
- [ ] Test semantic search.
- [ ] Ask the chatbot questions about meeting information.
- [ ] Test voice input through STT.
- [ ] Test audio responses through TTS.
- [ ] Restart the backend and confirm persisted data remains available.

## 9. Troubleshooting

| Problem | What to check |
|---|---|
| Database connection error | Confirm PostgreSQL is running, the port is correct, and `DATABASE_URL` contains the correct password and database name. |
| `vector` extension error | Confirm PGVector is installed for your PostgreSQL server version. |
| Ollama model not found | Run `ollama list` and check the configured model name. |
| Ollama memory error | Use a smaller model or hardware with more available memory. |
| Gemini API error | Verify the API key, model name, and API access. |
| Gnani STT/TTS error | Check credentials, endpoint configuration, request format, and service availability. |
| Frontend cannot reach backend | Confirm FastAPI is running and the frontend uses the correct backend URL. |
| Missing Python module | Activate the correct virtual environment and install the required dependencies. |
| Port already in use | Stop the conflicting process or configure another port. |

## 10. Security and Deployment Notes

This README describes a local development setup. Before making the application publicly accessible:

- Implement authentication and authorization.
- Ensure users can only access their own meetings and related records.
- Protect API credentials and database access.
- Configure secure storage for uploaded recordings.
- Use production server settings instead of development reload mode.
- Configure HTTPS and appropriate hosting.
- Configure database backups and persistent storage.


## Future Development

1. **Real-Time Meeting Recording:** Capture meeting audio directly from the application and process it while the meeting is taking place.
2. **Real-Time Agent Conversations:** Enable low-latency, spoken conversations with the Meeting Agent during an ongoing meeting.
3. **Persistent Audio Responses:** Store generated audio in suitable file or object storage and associate it with the relevant chat message so it can be replayed after refresh.

## Project Goal

Allen Meeting Assistant aims to make meetings easier to understand and follow up on by combining automated meeting analysis, semantic retrieval, conversational question answering, voice interaction, and actionable task management in one workspace.
