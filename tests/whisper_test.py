from faster_whisper import WhisperModel
import sounddevice as sd
from scipy.io.wavfile import write

SAMPLE_RATE = 16000
RECORD_SECONDS = 5
AUDIO_FILE = "test_audio.wav"

print("Loading Whisper model...")
model = WhisperModel("base", device="cpu", compute_type="int8")

print("Speak now...")
recording = sd.rec(
    int(RECORD_SECONDS * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16"
)

sd.wait()
write(AUDIO_FILE, SAMPLE_RATE, recording)

print("Transcribing...")
segments, info = model.transcribe(AUDIO_FILE, beam_size=5)

text = ""
for segment in segments:
    text += segment.text

print("Whisper heard:")
print(text.strip())