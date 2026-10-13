# ============================================================
# TRANSCRIPTION:
# This file converts meeting audio/video into text using the Faster-Whisper model.
# ============================================================

from faster_whisper import WhisperModel
from backend.meeting.i_state import MeetingState, MeetingKnowledge


class WhisperTranscriber:

    def __init__(self):

        # Load Whisper model only once.
        # "base" gives us a reasonable balance between
        # speed and transcription quality.
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def whisper_node(self, state: MeetingState):

        # Get the audio file path from the shared LangGraph state.
        print("Transcribing Audio...")

        audio_path = state["audio_path"]

        # Transcribe the audio file using Whisper.
        segments, info = self.model.transcribe(audio_path)

        transcript = ""

        # Combine all Whisper segments into one transcript.
        for segment in segments:
            transcript += segment.text + " "

        print("Transcription Completed")

        # Send the transcript back to the LangGraph state.
        return {
            "transcript": transcript
        }