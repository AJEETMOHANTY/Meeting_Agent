
import base64
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


class VoiceTextToSpeech:
    def __init__(self):
        self.api_key = os.getenv("GNANI_API_KEY")

        if not self.api_key:
            raise RuntimeError("GNANI_API_KEY is missing from the environment.")

        self.api_url = "https://api.vachana.ai/api/v1/tts/sse"
        self.model = "timbre-v2.5"
        self.voice = "Kaveri"
        self.language = "en-IN"
        self.speed = 1.0

    def stream_audio(self, text: str):
        if not text or not text.strip():
            raise ValueError("Text for speech generation cannot be empty.")

        payload = {
            "text": text.strip(),
            "model": self.model,
            "voice": self.voice,
            "language": self.language,
            "speed": self.speed,
            "audio_config": {
                "sample_rate": 48000,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        }

        with requests.post(
            self.api_url,
            headers={
                "X-API-Key-ID": self.api_key,
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            json=payload,
            stream=True,
            timeout=(10, 60),
        ) as response:
            response.raise_for_status()

            event_name = None

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    event_name = None
                    continue

                if line.startswith("event:"):
                    event_name = line[len("event:"):].strip()
                    continue

                if not line.startswith("data:"):
                    continue

                data_text = line[len("data:"):].strip()

                try:
                    event_data = json.loads(data_text)
                except json.JSONDecodeError as error:
                    raise RuntimeError(
                        "Gnani returned an invalid SSE event."
                    ) from error

                if event_name == "error":
                    raise RuntimeError(
                        f"Gnani TTS error: {event_data}"
                    )

                if event_name == "chunk":
                    encoded_audio = event_data.get("audio", "")
                    if encoded_audio:
                        yield base64.b64decode(encoded_audio)

                elif event_name == "complete":
                    return

    def generate_audio(self, text: str) -> bytes:
        # Convenience method for testing: combine all received chunks.
        return b"".join(self.stream_audio(text))
