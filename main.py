# ============================================================
# Friday AI Assistant
# A voice-controlled desktop assistant with app opening,
# routines, Edge TTS voice, and Whisper speech recognition.
# ============================================================


# ----------------------------
# Imports
# ----------------------------
import tts
import stt
import actions


# ----------------------------
# Command Router
# ----------------------------
def process_command(query):
    """
    Decides what Friday should do with the user's command.
    """

    if actions.handle_routine_command(query):
        return

    if "time" in query:
        actions.tell_time()

    elif "quack" in query:
        actions.ducks()

    elif "sleep" in query:
        tts.speak("All systems going idle sir.")
        return "sleep"

    elif "shutdown" in query:
        tts.speak("All systems going offline. Goodbye sir.")
        return "shutdown"

    elif "open" in query:
        actions.handle_open_command(query)

    elif "thank you" in query:
        tts.speak("My pleasure.")

    elif "search" in query:
        actions.search_wikipedia(query)

    elif "play" in query:
        actions.play_on_youtube(query)

    elif "type" in query:
        actions.typing_mode()

    elif "joke" in query:
        actions.tell_joke()

    else:
        tts.speak("I heard you, but I do not know that command yet.")


# ----------------------------
# Main Program
# ----------------------------
if __name__ == "__main__":
    actions.wish_user()
    tts.speak("Friday is online. What would you like to do today?")

    while True:
        query = stt.listen_for_command()

        if query == "none":
            continue

        if not stt.has_wake_word(query):
            print(f"Wake word not detected in: {query}")
            continue

        command = stt.remove_wake_word(query)

        if command == "":
            tts.speak("Yes sir?")
            command = stt.listen_for_command()

            if command == "none":
                tts.speak("I did not catch that")
                continue

        result = process_command(command)

        if result == "sleep":
            break

        if result == "shutdown":
            quit()