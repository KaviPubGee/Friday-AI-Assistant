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
import uuid

async def speak_async(audio, filename):
    """
    Creates a voice audio file using Edge TTS.
    """
    communicate = edge_tts.Communicate(audio, config.VOICE)
    await communicate.save(filename)


def speak(audio):
    """
    Makes Friday speak using Edge TTS.
    """
    print(f"Friday: {audio}")
    
    # Generate unique filename so background threads (timers) don't crash the main thread
    unique_file = f"friday_voice_{uuid.uuid4().hex}.mp3"

    try:
        asyncio.run(speak_async(audio, unique_file))
        playsound(unique_file)

        if os.path.exists(unique_file):
            os.remove(unique_file)

    except Exception as e:
        print("Voice error:", e)

