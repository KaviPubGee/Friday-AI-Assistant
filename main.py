# ============================================================
# Friday AI Assistant
# A voice-controlled desktop assistant with app opening,
# routines, Edge TTS voice, and Whisper speech recognition.
# ============================================================

import tts
import stt
import actions
import ai_brain
import memory
import reminders
import briefing


def conversation_should_end(query):
    end_phrases = [
        "bye",
        "goodbye",
        "that's all",
        "that is all",
        "stop talking",
        "end conversation",
        "see you later",
        "never mind",
        "go to sleep",
        "stand by"
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
# Command Router (Now 100% AI Driven)
# ----------------------------
def process_command(query, conversation_history):
    """
    Decides what Friday should do with the user's command based on the AI JSON output.
    """
    if conversation_history and is_follow_up(query):
        reply = ai_brain.chat_with_ai(query, conversation_history)
        tts.speak(reply)
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": reply})
        return "chat"

    print("Asking AI brain for intent...")
    command = ai_brain.understand_with_ai(query)
    intent = command.get("intent", "unknown")
    
    print("AI Brain decided intent:", intent)

    if intent == "run_routine":
        actions.run_routine(command.get("routine", ""))

    elif intent == "open_app":
        actions.handle_open_command(command.get("app", ""))

    elif intent == "tell_time":
        actions.tell_time()
        
    elif intent == "weather":
        actions.get_weather()

    elif intent == "ducks":
        actions.ducks()

    elif intent == "sleep":
        tts.speak("All systems going idle sir.")
        memory.save_memory(conversation_history)
        return "sleep"

    elif intent == "shutdown":
        tts.speak("All systems going offline. Goodbye sir.")
        memory.save_memory(conversation_history)
        return "shutdown"

    elif intent == "thanks":
        tts.speak("My pleasure.")

    elif intent == "search_wikipedia":
        actions.search_wikipedia(command.get("query", ""))

    elif intent == "play_media":
        actions.play_media(command.get("query", ""), command.get("platform", ""))

    elif intent == "typing_mode":
        actions.typing_mode()

    elif intent == "joke":
        joke = actions.tell_joke()
        conversation_history.append({
            "role": "assistant",
            "content": f"I told this joke: {joke}"
        })
        return "chat"
        
    elif intent == "volume_control":
        actions.volume_control(command.get("action", ""))
        
    elif intent == "screenshot":
        actions.take_screenshot()
        
    elif intent == "set_reminder":
        reminders.set_reminder(command.get("message", ""), int(command.get("delay_seconds", 60)))
        
    elif intent == "briefing":
        briefing.get_morning_briefing()
        
    elif intent == "play_game":
        game = command.get("game", "")
        actions.handle_open_command(game)
        tts.speak(f"Enjoy your game of {game}, sir. I will shut down now to save system resources.")
        memory.save_memory(conversation_history)
        return "shutdown"

    else:
        # Unknown intent: let the AI handle it as a normal conversation
        conversation_history.append({"role": "user", "content": query})
        reply = ai_brain.chat_with_ai(query, conversation_history)
        tts.speak(reply)
        conversation_history.append({"role": "assistant", "content": reply})
        return "chat"

    return "command"


# ----------------------------
# Main Program
# ----------------------------
if __name__ == "__main__":
    actions.wish_user()
    
    tts.speak("Would you like your morning briefing?")
    choice = stt.listen_for_command()
    if choice != "none" and ("yes" in choice or "sure" in choice or "please" in choice):
        briefing.get_morning_briefing()
    else:
        tts.speak("Very well. What would you like to do today?")

    conversation_active = True
    conversation_history = memory.load_memory()

    while True:
        query = stt.listen_for_command()

        if query == "none":
            continue

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
            memory.save_memory(conversation_history)
            continue

        result = process_command(command, conversation_history)

        if result in ("chat", "command"):
            conversation_active = True

        if result == "sleep":
            conversation_active = False
            conversation_history.clear()
            break

        if result == "shutdown":
            quit()