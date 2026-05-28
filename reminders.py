import threading
import time
import tts

def _reminder_thread(message, delay_seconds):
    """Sleeps for the delay, then speaks the reminder."""
    time.sleep(delay_seconds)
    tts.speak(f"Reminder: {message}")

def set_reminder(message, delay_seconds):
    """
    Spawns a background thread that will wait for the delay and then alert the user.
    delay_seconds can be a string or int — we handle both.
    """
    try:
        delay = int(float(str(delay_seconds)))
    except (ValueError, TypeError):
        delay = 60  # Default to 1 minute if parsing fails

    minutes = delay // 60
    seconds = delay % 60

    if minutes > 0:
        time_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        time_str = f"{seconds} second{'s' if seconds != 1 else ''}"

    tts.speak(f"Reminder set for {time_str}.")
    thread = threading.Thread(target=_reminder_thread, args=(message, delay), daemon=True)
    thread.start()
