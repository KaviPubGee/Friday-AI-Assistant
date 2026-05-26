# ============================================================
# Friday AI Assistant
# A voice-controlled desktop assistant with app opening,
# routines, Edge TTS voice, and Whisper speech recognition.
# ============================================================


# ----------------------------
# Imports
# ----------------------------
import asyncio
import datetime
import json
import os

import edge_tts
import pyautogui
import pyjokes
import pywhatkit
import sounddevice as sd
import speech_recognition as sr
import wikipedia

from faster_whisper import WhisperModel
from playsound import playsound
from scipy.io.wavfile import write


# ----------------------------
# Assistant Settings
# ----------------------------
ASSISTANT_NAME = "friday"
WAKE_WORDS = [
    "friday",
    "fridays",
    "friday.",
    "friday,",
    "stridey",
    "pride it",
    "fridaye"
]

# Edge TTS voice
VOICE = "en-US-AriaNeural"
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
    "let's get to work": "work mode",
    "lets get to work": "work mode",
    "time to work": "work mode",
    "start work": "work mode",
    "dev mode": "work mode",
    "development mode": "work mode"
}


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


# ----------------------------
# Whisper Model Loading
# ----------------------------
print("Loading Whisper model...")
whisper_model = WhisperModel(
    WHISPER_MODEL_SIZE,
    device=WHISPER_DEVICE,
    compute_type=WHISPER_COMPUTE_TYPE
)
print("Whisper model loaded.")


# ----------------------------
# Voice System
# ----------------------------
async def speak_async(audio):
    """
    Creates a voice audio file using Edge TTS.
    """
    communicate = edge_tts.Communicate(audio, VOICE)
    await communicate.save(VOICE_AUDIO_FILE)


def speak(audio):
    """
    Makes Friday speak using Edge TTS.
    """
    print(f"Friday: {audio}")

    try:
        asyncio.run(speak_async(audio))
        playsound(VOICE_AUDIO_FILE)

        if os.path.exists(VOICE_AUDIO_FILE):
            os.remove(VOICE_AUDIO_FILE)

    except Exception as e:
        print("Voice error:", e)


# ----------------------------
# Speech Recognition
# ----------------------------
def commands_whisper():
    """
    Records audio for a fixed amount of time,
    then uses Whisper to convert speech to text.
    """
    print("Listening with Whisper...")

    try:
        recording = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )

        sd.wait()
        write(COMMAND_AUDIO_FILE, SAMPLE_RATE, recording)

        print("Recognizing with Whisper...")
        segments, info = whisper_model.transcribe(
            COMMAND_AUDIO_FILE,
            beam_size=5
        )

        query = ""

        for segment in segments:
            query += segment.text

        query = query.lower().strip()

        if query == "":
            print("Whisper heard nothing.")
            return "none"

        print(f"You said: {query}\n")
        return query

    except Exception as e:
        print("Whisper command error:", e)
        return "none"


def commands_google():
    """
    Backup speech recognition using Google's recognizer.
    This is faster, but may be less accurate depending on accent/noise.
    """
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Calibrating microphone...")
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.5
        recognizer.adjust_for_ambient_noise(source, duration=0.8)

        print("Listening...")

        try:
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=12)

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return "none"

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-GB")
        query = query.lower().strip()

        print(f"You said: {query}\n")
        return query

    except sr.UnknownValueError:
        print("Could not understand audio.")
        return "none"

    except sr.RequestError:
        print("Speech recognition service error.")
        return "none"


def listen_for_command():
    """
    Chooses which speech recognition system Friday should use.
    """
    if RECOGNITION_MODE == "whisper":
        return commands_whisper()

    return commands_google()


# ----------------------------
# Basic Assistant Actions
# ----------------------------
def wish_user():
    """
    Greets the user based on the time of day.
    """
    hour = int(datetime.datetime.now().hour)

    if 0 <= hour < 12:
        speak("Good morning sir.")

    elif 12 <= hour < 17:
        speak("Good afternoon sir.")

    else:
        speak("Good evening sir.")


def tell_time():
    """
    Tells the current time.
    """
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"It's currently {current_time}.")
    print(current_time)


def ducks():
    """
    Very important duck command.
    """
    speak("Ducks are cool!")


def tell_joke():
    """
    Tells a programming joke.
    """
    joke = pyjokes.get_joke()
    print(joke)
    speak(joke)


# ----------------------------
# App Opening
# ----------------------------
def open_app(app_name):
    """
    Opens an app if its path exists in APPS.
    """
    if app_name in APPS:
        speak(f"Opening {app_name}.")
        os.startfile(APPS[app_name])

    else:
        speak(f"I do not have the app location for {app_name} yet.")


def handle_open_command(query):
    """
    Handles commands like:
    - Friday open unity
    - Friday open vs code
    - Friday open visual studio code
    """

    # First check official app names.
    for app_name in APPS:
        if app_name in query:
            open_app(app_name)
            return

    # Then check app aliases.
    for alias, app_name in APP_ALIASES.items():
        if alias in query:
            open_app(app_name)
            return

    speak("I do not have that app location yet.")


# ----------------------------
# Routines
# ----------------------------
def run_routine(routine_name):
    """
    Runs a saved routine.
    A routine is a list of apps that Friday opens one by one.
    """
    if routine_name not in ROUTINES:
        speak(f"I do not know the routine {routine_name}.")
        return

    speak(f"{routine_name} activated.")

    for app_name in ROUTINES[routine_name]:
        open_app(app_name)


def handle_routine_command(query):
    """
    Checks if the user's command matches a routine or routine alias.
    Returns True if a routine was found and handled.
    """
    # First check official routine names.
    for routine_name in ROUTINES:
        if routine_name in query:
            run_routine(routine_name)
            return True

    # Then check routine aliases.
    for alias, routine_name in ROUTINE_ALIASES.items():
        if alias in query:
            run_routine(routine_name)
            return True

    return False


# ----------------------------
# Internet / Utility Commands
# ----------------------------
def search_wikipedia(query):
    """
    Searches Wikipedia using the cleaned user query.
    """
    speak("Searching Wikipedia.")

    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("search", "")
    query = query.replace("on wikipedia", "")
    query = query.replace("wikipedia", "")
    query = query.strip()

    try:
        results = wikipedia.summary(query, sentences=1)
        speak("According to Wikipedia.")
        print(results)
        speak(results)

    except Exception:
        speak("Sorry, I could not find anything for that.")
        print("Sorry, I could not find anything for that.")


def play_on_youtube(query):
    """
    Plays a YouTube video using pywhatkit.
    """
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("play", "")
    query = query.strip()

    speak(f"Playing {query}.")
    pywhatkit.playonyt(query)


def typing_mode():
    """
    Types whatever the user says until they say 'stop typing'.
    """
    speak("What should I write, sir?")

    while True:
        text_to_type = listen_for_command()

        if text_to_type == "stop typing":
            speak("Done, sir.")
            break

        if text_to_type != "none":
            pyautogui.write(text_to_type)


# ----------------------------
# Command Router
# ----------------------------
def process_command(query):
    """
    Decides what Friday should do with the user's command.
    """

    if handle_routine_command(query):
        return

    if "time" in query:
        tell_time()

    elif "quack" in query:
        ducks()

    elif "sleep" in query:
        speak("All systems going idle sir.")
        return "sleep"

    elif "shutdown" in query:
        speak("All systems going offline. Goodbye sir.")
        return "shutdown"

    elif "open" in query:
        handle_open_command(query)

    elif "thank you" in query:
        speak("Happy to help you sir.")

    elif "search" in query:
        search_wikipedia(query)

    elif "play" in query:
        play_on_youtube(query)

    elif "type" in query:
        typing_mode()

    elif "joke" in query:
        tell_joke()

    else:
        speak("I heard you, but I do not know that command yet.")


# ----------------------------
# Main Program
# ----------------------------
if __name__ == "__main__":
    speak("Friday is online. What would you like to do today?")

    while True:
        query = listen_for_command()

        if query == "none":
            continue

        wake_word_detected = any(
            wake_word in query for wake_word in WAKE_WORDS
        )

        if not wake_word_detected:
            print(f"Wake word not detected in: {query}")
            continue

        result = process_command(query)

        if result == "sleep":
            break

        if result == "shutdown":
            quit()