
import sounddevice as sd
from backend.voice.a_speech_to_text import VoiceSpeechToText
from backend.voice.b_text_to_speech import VoiceTextToSpeech

from langchain_core.messages import HumanMessage
from backend.meeting.h_agent import agent


class VoiceChatService:
    def __init__(self):
        self.speech_to_text = VoiceSpeechToText()
        self.text_to_speech = VoiceTextToSpeech()

        # Use your working microphone device.
        self.microphone_device = 2
        self.sample_rate = 16000

    def listen(self) -> str:
        print("\nSpeak now... (5 seconds)")

        audio = sd.rec(
            int(5 * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            device=self.microphone_device,
        )
        sd.wait()

        # Transcribe directly from memory; do not save a recording.
        return self.speech_to_text.transcribe(audio.flatten())
    
    def ask_agent(self, question: str, meeting_id: int) -> str:
        # Send the recognized question to the existing agent.
        result = agent.invoke({
            "messages": [HumanMessage(content=question)],
            "meeting_id": meeting_id,
        })

        # Get the agent's final response.
        answer = result["messages"][-1].content

        return answer
    
    
    def speak_response(self, answer) -> None:
        # Convert the agent's response into plain text.
        if isinstance(answer, list):
            answer = " ".join(
                item["text"]
                for item in answer
                if isinstance(item, dict) and item.get("type") == "text"
            )

        if not isinstance(answer, str):
            answer = str(answer)

        print(f"\nAllen: {answer}")
        self.text_to_speech.speak(answer)

