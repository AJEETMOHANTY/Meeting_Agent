
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class VoiceSpeechToText:
    def __init__(self):
        self.api_key = os.getenv("GNANI_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GNANI_API_KEY is missing from the environment."
            )

        self.api_url = "https://api.vachana.ai/stt/v3"

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        language_code: str = "en-IN",
        filename: str = "recording.wav",
    ) -> str:
        if not audio_bytes:
            raise ValueError("Audio recording is empty.")

        response = requests.post(
            self.api_url,
            headers={"X-API-Key-ID": self.api_key},
            files={
                "audio_file": (
                    filename,
                    audio_bytes,
                    "audio/wav",
                )
            },
            data={
                "language_code": language_code,
                "format": "transcribe",
            },
            timeout=60,
        )

        response.raise_for_status()
        result = response.json()

        if not result.get("success"):
            raise RuntimeError(
                f"Gnani transcription failed: {result}"
            )

        transcript = result.get("transcript", "").strip()

        if not transcript:
            raise RuntimeError(
                "Gnani returned an empty transcript."
            )

        return transcript
