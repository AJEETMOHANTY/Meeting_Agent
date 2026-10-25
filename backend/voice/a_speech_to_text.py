
import numpy as np
from faster_whisper import WhisperModel


class VoiceSpeechToText:
    def __init__(self):
        # Load Whisper once for local speech recognition.
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio: np.ndarray) -> str:
        # Convert microphone audio from int16 to float32.
        audio = audio.astype(np.float32) / 32768.0

        # Recognize speech directly from memory.
        segments, _ = self.model.transcribe(audio)

        return " ".join(
            segment.text.strip() for segment in segments
        ).strip()
