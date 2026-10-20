# ============================================================
# STEP C: TRANSCRIPT VALIDATION
# This file checks whether the transcript produced by
# Whisper is usable before sending it to the LLM.
# ============================================================
def validate_transcript(transcript: str) -> tuple[bool, str]:

    # Check if the transcript is empty.
    if not transcript:
        return False, "Transcript is empty."

    # Remove unnecessary spaces.
    transcript = transcript.strip()

    # Check again after removing spaces.
    if not transcript:
        return False, "Transcript contains only whitespace."

    # Count the number of words.
    word_count = len(transcript.split())

    # A very short transcript probably isn't useful.
    if word_count < 10:
        return False, f"Transcript is too short ({word_count} words). Minimum 10 words required."

    # Everything looks okay.
    return True, f"Transcript is usable ({word_count} words)."
