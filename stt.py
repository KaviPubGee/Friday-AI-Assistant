# ----------------------------
# Imports
# ----------------------------
import speech_recognition as sr
from faster_whisper import WhisperModel
import config

print("Loading Whisper model...")
whisper_model = WhisperModel(
    config.WHISPER_MODEL_SIZE,
    device=config.WHISPER_DEVICE,
    compute_type=config.WHISPER_COMPUTE_TYPE
)
print("Whisper model loaded.")


def commands_whisper():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Calibrating microphone...")
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.0 
        recognizer.adjust_for_ambient_noise(source, duration=0.8)

        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return "none"

    try:
        print("Recognizing with Whisper...")
        with open(config.COMMAND_AUDIO_FILE, "wb") as file:
            file.write(audio.get_wav_data())
            
        segments, info = whisper_model.transcribe(config.COMMAND_AUDIO_FILE, beam_size=5)

        query = ""
        for segment in segments:
            query += segment.text

        query = query.lower().strip()

        if query == "":
            return "none"

        print(f"You said: {query}\n")
        return query

    except Exception as e:
        print("Whisper command error:", e)
        return "none"


def has_wake_word(query):
    return any(wake_word in query for wake_word in config.WAKE_WORDS)

def remove_wake_word(query):
    for wake_word in config.WAKE_WORDS:
        query = query.replace(wake_word, "")
    return query.strip()

def listen_for_command():
    return commands_whisper()