# ============================================================
# Friday AI Assistant
# A voice-controlled desktop assistant with app opening,
# routines, Edge TTS voice, and Whisper speech recognition.
# ============================================================

import tts
import stt
import actions
import brain
import ai_brain


def conversation_should_end(query):
    end_phrases = [
        "bye",
        "goodbye",
        "that's all",
        "that is all",
        "stop talking",
        "end conversation",
        "see you later",
        "never mind"
        "thankyou"
        "thank you"
        "thanks"
    ]
    return any(phrase in query for phrase in end_phrases)


def is_follow_up(query):
    follow_up_phrases = [
        "explain",
        "explain it",
        "explain that",
        "explain the joke",
        "what does that mean",
        "what do you mean",
        "why",
        "how come",
        "tell me more",
        "continue",
        "go on",
        "elaborate"
    ]
    return any(phrase in query for phrase in follow_up_phrases)


# ----------------------------
# Command Router
# ----------------------------
def process_command(query, conversation_history):
    """
    Decides what Friday should do with the user's command.
    """

    # FIX 1: If we are mid-conversation and the user says something like
    # "explain that" or "why", skip the intent router entirely and go
    # straight to the AI with the full conversation history.
    # This is how she remembers what joke she just told!
    if conversation_history and is_follow_up(query):
        reply = ai_brain.chat_with_ai(query, conversation_history)
        tts.speak(reply)

        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": reply})

        return "chat"

    command = brain.understand_command(query)
    intent = command["intent"]

    if intent == "run_routine":
        actions.run_routine(command["routine"])

    elif intent == "open_app":
        actions.open_app(command["app"])

    elif intent == "tell_time":
        actions.tell_time()

    elif intent == "ducks":
        actions.ducks()

    elif intent == "sleep":
        tts.speak("All systems going idle sir.")
        return "sleep"

    elif intent == "shutdown":
        tts.speak("All systems going offline. Goodbye sir.")
        return "shutdown"

    elif intent == "thanks":
        tts.speak("My pleasure.")

    elif intent == "search_wikipedia":
        actions.search_wikipedia(command["query"])

    elif intent == "play_youtube":
        actions.play_on_youtube(command["query"])

    elif intent == "typing_mode":
        actions.typing_mode()

    elif intent == "joke":
        # Tell the joke AND save it to conversation history
        # so when the user says "explain the joke", Friday knows what she said!
        joke = actions.tell_joke()
        conversation_history.append({
            "role": "assistant",
            "content": f"I told this joke: {joke}"
        })
        return "chat"

    else:
        # Unknown intent: let the AI handle it as a normal conversation
        conversation_history.append({"role": "user", "content": query})
        reply = ai_brain.chat_with_ai(query, conversation_history)
        tts.speak(reply)
        conversation_history.append({"role": "assistant", "content": reply})
        return "chat"

    # FIX 2: For all normal commands (time, open app, etc.),
    # we return "command" so the main loop knows something happened
    # and can keep the conversation active.
    return "command"


# ----------------------------
# Main Program
# ----------------------------
if __name__ == "__main__":
    actions.wish_user()
    tts.speak("Friday is online. What would you like to do today?")

    conversation_active = False
    conversation_history = []

    while True:
        query = stt.listen_for_command()

        if query == "none":
            continue

        # FIX 3: Only require wake word if we are NOT already in a conversation.
        # If conversation_active is True, Friday listens directly without needing
        # the user to say "Friday" every single time!
        if not conversation_active:
            if not stt.has_wake_word(query):
                print(f"Wake word not detected in: {query}")
                continue
            command = stt.remove_wake_word(query)
        else:
            command = query

        if command == "":
            tts.speak("Yes sir?")
            command = stt.listen_for_command()

            if command == "none":
                tts.speak("I did not catch that")
                continue

        # Check if the user wants to end the conversation
        if conversation_should_end(command):
            tts.speak("Understood, sir.")
            conversation_active = False
            conversation_history.clear()
            continue

        result = process_command(command, conversation_history)

        # FIX 4: Keep conversation alive after ANY successful command,
        # not just AI chat. So after she tells the time, she still listens
        # without needing the wake word again.
        if result in ("chat", "command"):
            conversation_active = True

        if result == "sleep":
            conversation_active = False
            conversation_history.clear()
            break

        if result == "shutdown":
            quit()