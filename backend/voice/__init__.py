# Convert a user's recorded voice into text.
# This module is separate from the meeting transcription pipeline.

from faster_whisper import WhisperModel


class VoiceSpeechToText:
    def __init__(self):
        # Load the local Whisper model.
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path: str) -> str:
        # Convert the recorded audio into text.
        segments, info = self.model.transcribe(audio_path)

        # Combine all recognized speech into one string.
        transcript = " ".join(
            segment.text.strip() for segment in segments
        ).strip()

        return transcript