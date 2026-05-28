import threading
import time
import tts

def _reminder_thread(message, delay_seconds):
    """Sleeps for the delay, then speaks the reminder."""
    time.sleep(delay_seconds)
    tts.speak(f"Sir, I have a reminder for you: {message}")

def set_reminder(message, delay_seconds):
    """
    Spawns a background thread that will wait for the delay and then alert the user.
    This doesn't freeze the main assistant loop.
    """
    tts.speak(f"Reminder set for {message}.")
    thread = threading.Thread(target=_reminder_thread, args=(message, delay_seconds), daemon=True)
    thread.start()
