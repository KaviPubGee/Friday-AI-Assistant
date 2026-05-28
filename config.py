# ----------------------------
# Imports
# ----------------------------
import json

# ----------------------------
# Assistant Settings
# ----------------------------
ASSISTANT_NAME = "friday"
WAKE_WORDS = [
    "friday",
    "fridays",
    "freddy",
    "fry day",
    "freeday",
    "hey friday",
    "hi friday",
    "ok friday",
    "friday.",
    "friday,",
    "stridey",
    "pride it",
    "fridaye",
    "ryday",
    "phriday"
]

AI_BRAIN_ENABLED = True
AI_PROVIDER = "ollama"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/chat"

# Edge TTS voice
VOICE = "en-GB-SoniaNeural"
VOICE_AUDIO_FILE = "friday_voice.mp3"

# Choose which speech recognition system to use:
# "whisper" = local Whisper recognition
# "google" = speech_recognition Google recognizer
RECOGNITION_MODE = "whisper"


# ----------------------------
# Whisper Settings
# ----------------------------
WHISPER_MODEL_SIZE = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

SAMPLE_RATE = 16000
RECORD_SECONDS = 6
COMMAND_AUDIO_FILE = "command.wav"


# ----------------------------
# Default Data
# ----------------------------
DEFAULT_APPS = {
    "unity": "C:/Program Files/Unity Hub/Unity Hub.exe"
}

APP_ALIASES = {
    "visual studio code": "vscode",
    "vs code": "vscode",
    "code": "vscode",
    "unity hub": "unity"
}

DEFAULT_ROUTINES = {
    "work mode": ["unity"]
}

ROUTINE_ALIASES = {
    "get to work": "work mode",
    "we get to work": "work mode",
    "let us get to work": "work mode",
    "let's work": "work mode",
    "lets work": "work mode",
    "work today": "work mode",
    "start working": "work mode",
    "coding mode": "work mode",
    "game dev mode": "work mode",
}

ALLOWED_INTENTS = [
    "open_app",
    "run_routine",
    "tell_time",
    "play_youtube",
    "search_wikipedia",
    "joke",
    "thanks",
    "sleep",
    "shutdown",
    "typing_mode",
    "ducks",
    "unknown"
]


# ----------------------------
# Config Loading
# ----------------------------
def load_json_file(file_name, default_data):
    """
    Loads data from a JSON file.
    If the file does not exist, Friday uses default data instead.
    """
    try:
        with open(file_name, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        return default_data


APPS = load_json_file("apps.json", DEFAULT_APPS)
ROUTINES = load_json_file("routines.json", DEFAULT_ROUTINES)

