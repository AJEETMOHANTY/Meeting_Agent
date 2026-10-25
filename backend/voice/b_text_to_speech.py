# Converts the agent's response into an audio file.

# Convert text into speech locally.
# No paid API or internet connection is required.

import pyttsx3


class VoiceTextToSpeech:
    def __init__(self):
        # Initialize the computer's local speech engine.
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)
        self.engine.setProperty("volume", 1.0)

    def speak(self, text: str) -> None:
        # Speak the provided text through the speakers.
        if not text.strip():
            return

        self.engine.say(text)
        self.engine.runAndWait()


if __name__ == "__main__":
    # Test speech output independently.
    speaker = VoiceTextToSpeech()
    speaker.speak("Hello! Your Allen voice assistant is working.")
