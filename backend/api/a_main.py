
from fastapi import FastAPI
from backend.api.b_meetings import router as meetings_router
from backend.api.c_chat import router as chat_router  # Imports chatbot endpoints.

from fastapi import UploadFile, File, Form, HTTPException
from backend.voice.a_speech_to_text import VoiceSpeechToText

from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from backend.voice.b_text_to_speech import VoiceTextToSpeech


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


@app.post("/voice/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...),
    language_code: str = Form("en-IN"),
):
    try:
        audio_bytes = await audio.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=400,
                detail="Audio recording is empty.",
            )

        stt = VoiceSpeechToText()

        transcript = stt.transcribe_bytes(
            audio_bytes=audio_bytes,
            language_code=language_code,
            filename=audio.filename or "recording.wav",
        )

        return {
            "transcript": transcript
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Voice transcription failed: {error}",
        ) from error


class SpeechRequest(BaseModel):
    text: str

# BaseModel validates the text sent to the API.

@app.post("/voice/synthesize/stream")
def synthesize_voice_stream(request: SpeechRequest):
    try:
        tts = VoiceTextToSpeech()

        def audio_chunks():
            # Forward each decoded audio chunk as Gnani produces it.
            yield from tts.stream_audio(request.text)

        return StreamingResponse(
            audio_chunks(),
            media_type="application/octet-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Content-Type-Options": "nosniff",
            },
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
