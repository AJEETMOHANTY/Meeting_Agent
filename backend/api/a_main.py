
from fastapi import FastAPI
from backend.api.b_meetings import router as meetings_router
from backend.api.c_chat import router as chat_router  # Imports chatbot endpoints.

app = FastAPI(
    title="Allen V2",
    description="AI Meeting Intelligence Platform",
    version="1.0.0",
)

app.include_router(meetings_router)
app.include_router(chat_router)  # Connects chatbot endpoints to FastAPI.


@app.get("/")
def home():
    return {
        "message": "Allen V2 API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
