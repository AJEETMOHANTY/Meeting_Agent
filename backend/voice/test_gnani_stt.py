
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GNANI_API_KEY")
audio_path = Path("voice_test.wav")

if not api_key:
    raise RuntimeError("GNANI_API_KEY is missing from .env")

if not audio_path.exists():
    raise FileNotFoundError(audio_path)

with audio_path.open("rb") as audio_file:
    response = requests.post(
        "https://api.vachana.ai/stt/v3",
        headers={"X-API-Key-ID": api_key},
        files={
            "audio_file": (
                audio_path.name,
                audio_file,
                "audio/wav",
            )
        },
        data={
            "language_code": "en-IN",
            "format": "transcribe",
        },
        timeout=60,
    )

print("HTTP status:", response.status_code)
print("Response:", response.text)

response.raise_for_status()
print("Transcript:", response.json().get("transcript", ""))
