
from backend.voice.c_voice_service import VoiceChatService


def main():
    voice = VoiceChatService()
    meeting_id = int(input("Enter meeting ID: "))

    print("\nAllen Voice Chat")
    print("1. Speak your question")
    print("2. Type your question")

    choice = input("Choose input mode (1/2): ").strip()

    if choice == "1":
        # Spoken questions default to spoken answers.
        question = voice.listen()
        response_mode = "audio"

    elif choice == "2":
        # Typed questions default to text answers.
        question = input("Type your question: ").strip()
        response_mode = "text"

    else:
        print("Invalid choice.")
        return

    if not question:
        print("No question detected.")
        return

    print(f"\nYou asked: {question}")

    answer = voice.ask_agent(question, meeting_id)

    if response_mode == "audio":
        voice.speak_response(answer)
    else:
        print(f"\nAllen: {answer}")


if __name__ == "__main__":
    main()
