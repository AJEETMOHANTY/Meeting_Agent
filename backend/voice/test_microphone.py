# Test microphone recording from the terminal.

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

duration = 5  # Record for 5 seconds
sample_rate = 16000

print("Speak now...")

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="int16",
    device=2
)

sd.wait()

write("voice_test.wav", sample_rate, audio)
print("Maximum audio level:", np.max(np.abs(audio)))
print("Average audio level:", np.mean(np.abs(audio)))


print("Recording saved as voice_test.wav")
