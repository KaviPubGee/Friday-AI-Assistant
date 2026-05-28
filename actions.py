# ----------------------------
# Imports
# ----------------------------
import datetime
import os
import pyautogui
import pyjokes
import pywhatkit
import wikipedia

import config
import tts
import stt


def wish_user():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        tts.speak("Good morning sir.")
    elif 12 <= hour < 17:
        tts.speak("Good afternoon sir.")
    else:
        tts.speak("Good evening sir.")


def tell_time():
    current_time = datetime.datetime.now().strftime("%I:%M:%p").replace(":", " ")
    tts.speak(f"It's currently {current_time}.")
    print(current_time)


def ducks():
    tts.speak("Ducks are cool!")


def tell_joke():
    joke = pyjokes.get_joke()
    print(joke)
    tts.speak(joke)
    return joke


def open_app(app_name):
    if app_name in config.APPS:
        tts.speak(f"Opening {app_name}.")
        os.startfile(config.APPS[app_name])
    else:
        tts.speak(f"I do not have the app location for {app_name} yet.")


def handle_open_command(query):
    for app_name in config.APPS:
        if app_name in query:
            open_app(app_name)
            return
    for alias, app_name in config.APP_ALIASES.items():
        if alias in query:
            open_app(app_name)
            return
    tts.speak("I do not have that app location yet.")


def run_routine(routine_name):
    if routine_name not in config.ROUTINES:
        tts.speak(f"I do not know the routine {routine_name}.")
        return
    tts.speak(f"{routine_name} activated.")
    for app_name in config.ROUTINES[routine_name]:
        open_app(app_name)


def handle_routine_command(query):
    for routine_name in config.ROUTINES:
        if routine_name in query:
            run_routine(routine_name)
            return True
    for alias, routine_name in config.ROUTINE_ALIASES.items():
        if alias in query:
            run_routine(routine_name)
            return True
    return False


def search_wikipedia(query):
    tts.speak("Searching Wikipedia.")
    query = query.replace(config.ASSISTANT_NAME, "")
    query = query.replace("search", "")
    query = query.replace("on wikipedia", "")
    query = query.replace("wikipedia", "")
    query = query.strip()

    try:
        results = wikipedia.summary(query, sentences=1)
        tts.speak("According to Wikipedia.")
        print(results)
        tts.speak(results)
    except Exception:
        tts.speak("Sorry, I could not find anything for that.")
        print("Sorry, I could not find anything for that.")


def play_on_youtube(query):
    query = query.replace(config.ASSISTANT_NAME, "")
    query = query.replace("play", "")
    query = query.replace("put on", "")
    query = query.replace("start playing", "")
    query = query.replace("on youtube", "")
    query = query.replace("youtube", "")
    query = query.strip()

    if query == "":
        tts.speak("What should I play?")
        return
    
    tts.speak(f"Playing {query}.")
    pywhatkit.playonyt(query)


def typing_mode():
    tts.speak("What should I write, sir?")
    while True:
        text_to_type = stt.listen_for_command()
        if text_to_type == "stop typing":
            tts.speak("Done, sir.")
            break
        if text_to_type != "none":
            pyautogui.write(text_to_type)