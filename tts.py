# ----------------------------
# Imports
# ----------------------------
import asyncio
import os
import edge_tts
from playsound import playsound

import config


# ----------------------------
# Voice System
# ----------------------------
async def speak_async(audio):
    """
    Creates a voice audio file using Edge TTS.
    """
    communicate = edge_tts.Communicate(audio, config.VOICE)
    await communicate.save(config.VOICE_AUDIO_FILE)


def speak(audio):
    """
    Makes Friday speak using Edge TTS.
    """
    print(f"Friday: {audio}")

    try:
        asyncio.run(speak_async(audio))
        playsound(config.VOICE_AUDIO_FILE)

        if os.path.exists(config.VOICE_AUDIO_FILE):
            os.remove(config.VOICE_AUDIO_FILE)

    except Exception as e:
        print("Voice error:", e)

