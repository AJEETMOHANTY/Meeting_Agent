
from pathlib import Path

from backend.voice.b_text_to_speech import VoiceTextToSpeech


tts = VoiceTextToSpeech()

output_path = Path("gnani_tts_stream_test.wav")
total_bytes = 0
chunk_count = 0

with output_path.open("wb") as audio_file:
    for chunk in tts.stream_audio(
        "Hello! This is a streaming test of the Allen Meeting Intelligence Agent."
    ):
        audio_file.write(chunk)
        total_bytes += len(chunk)
        chunk_count += 1
        print(f"Received chunk {chunk_count}: {len(chunk)} bytes")

print(f"\nAudio saved to: {output_path.resolve()}")
print(f"Total chunks: {chunk_count}")
print(f"Total audio bytes: {total_bytes}")
