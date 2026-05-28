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


# --- GLOBAL MICROPHONE SETTINGS ---
# Creating this here instead of inside the function means Friday
# "remembers" the noise profile of your room and gets better at hearing
# you the longer the program runs!
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 300
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5
recognizer.pause_threshold = 3.0
recognizer.phrase_threshold = 0.3
recognizer.non_speaking_duration = 0.3

# We will calibrate it once globally when the program starts
print("Calibrating background noise...")
with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=2.0)
print(f"Calibration complete! Base noise level: {int(recognizer.energy_threshold)}")


def commands_whisper():
    with sr.Microphone() as source:
        print(f"Listening... (noise level: {int(recognizer.energy_threshold)})")

        try:
            audio = recognizer.listen(
                source,
                timeout=7,           # give up if no speech for 7 seconds
                phrase_time_limit=15 # max 15 seconds of speech per command
            )
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return "none"

    try:
        print("Recognizing with Whisper...")

        # Save audio to file for Whisper to read
        with open(config.COMMAND_AUDIO_FILE, "wb") as file:
            file.write(audio.get_wav_data(
                convert_rate=16000,  # Whisper works best at exactly 16000 Hz
                convert_width=2      # 16-bit audio — crisp without being heavy
            ))

        segments, info = whisper_model.transcribe(
            config.COMMAND_AUDIO_FILE,

            # beam_size: how many options Whisper considers before picking a word.
            # Higher = more accurate but slightly slower. 5 is the sweet spot.
            beam_size=5,

            # language: telling Whisper it's English so it doesn't waste time
            # guessing. This alone makes a noticeable speed and accuracy difference.
            language="en",

            # vad_filter: Voice Activity Detection. Whisper will automatically
            # ignore silent parts and background noise in the recording.
            vad_filter=True,

            # vad_parameters: fine-tuning the silence filter.
            # min_silence_duration_ms: only cut silence if it's longer than 500ms.
            # This prevents Whisper from cutting mid-sentence pauses.
            vad_parameters={"min_silence_duration_ms": 500},

            # condition_on_previous_text: if True, Whisper tries to make each word
            # fit with what came before. Can cause hallucinations on short commands,
            # so we turn it off for a voice assistant.
            condition_on_previous_text=False,
            
            # --- Hallucination Fixes ---
            # If the text is highly repetitive (like Whisper hallucinating "Thank you, thank you"), reject it.
            compression_ratio_threshold=2.4,
            
            # If the audio has a high probability of being silence/noise, reject it.
            # 0.6 is strict enough to block static hums that Whisper turns into words.
            no_speech_threshold=0.6
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


def has_wake_word(query):
    return any(wake_word in query for wake_word in config.WAKE_WORDS)

def remove_wake_word(query):
    for wake_word in config.WAKE_WORDS:
        query = query.replace(wake_word, "")
    return query.strip()

def listen_for_command():
    return commands_whisper()